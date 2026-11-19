import logging

from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.email import ActivationEmail
from djoser.views import UserViewSet
from recipes.models import (
    Ingredient,
    Recipe,
    RecipeIngredient,
    Subscription,
    Tag,
)
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.filters import RecipeFilter
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    AvatarSerializer,
    FavoriteSerializer,
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    ShoppingCartSerializer,
    SubscriptionCreateSerializer,
    SubscriptionSerializer,
    TagSerializer,
)

User = get_user_model()


logger = logging.getLogger(__name__)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_permissions(self):
        if self.action in (
            "favorite", "shopping_cart", "download_shopping_cart"
        ):
            return [IsAuthenticated()]
        if self.action == "get_link":
            return [AllowAny()]
        return [IsAuthorOrReadOnly()]

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=("post", "delete"),
        permission_classes=(IsAuthenticated,)
    )
    def _add_or_remove(
        self, request, serializer_class, related_name, not_found_message
    ):
        recipe = self.get_object()
        if request.method == "POST":
            serializer = serializer_class(
                data={"recipe": recipe.pk},
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        deleted, _ = getattr(request.user, related_name).filter(
            recipe=recipe
        ).delete()
        if not deleted:
            raise ValidationError(not_found_message)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=("post", "delete"),
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk=None):
        return self._add_or_remove(
            request, FavoriteSerializer, "favorites",
            "Рецепта нет в избранном.",
        )

    @action(
        detail=True,
        methods=("post", "delete"),
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        return self._add_or_remove(
            request, ShoppingCartSerializer, "shopping_carts",
            "Рецепта нет в списке покупок.",
        )

    @action(
        detail=False, methods=["get"], permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredients = (
            RecipeIngredient.objects.filter(
                recipe__shopping_carts__user=request.user
            )
            .values("ingredient__name", "ingredient__measurement_unit")
            .annotate(total=Sum("amount"))
            .order_by("ingredient__name")
        )
        lines = [
            f"{item['ingredient__name']} "
            f"({item['ingredient__measurement_unit']}) — {item['total']}"
            for item in ingredients
        ]
        response = HttpResponse(
            "\n".join(lines), content_type="text/plain; charset=utf-8"
        )
        response["Content-Disposition"] = (
            "attachment; filename='shopping_list.txt'"
        )
        return response


    @action(detail=True, methods=["get"], url_path="get-link")
    def get_link(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        url = request.build_absolute_uri(
            reverse("recipes:short-link", args=[recipe.short_link])
        )
        return Response({"short-link": url})


class IngredientViewSet(ReadOnlyModelViewSet):
    pagination_class = None
    permission_classes = (AllowAny,)
    serializer_class = IngredientSerializer

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        name_param = self.request.query_params.get("name")

        if name_param:
            queryset = queryset.filter(name__istartswith=name_param)

        return queryset


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (AllowAny,)


class AccountViewSet(UserViewSet):

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return super().get_permissions()

    def perform_create(self, serializer, *args, **kwargs):
        super().perform_create(serializer, *args, **kwargs)
        user = serializer.instance
        try:
            ActivationEmail(self.request, {"user": user}).send([user.email])
        except Exception:
            logger.exception(
                "Не удалось отправить письмо подтверждения на %s", user.email
            )

    @action(
        detail=False,
        methods=("put", "delete",),
        url_path="me/avatar",
        permission_classes=[IsAuthenticated],
    )
    def avatar(self, request):
        user = request.user
        if request.method == "DELETE":
            if user.avatar:
                user.avatar.delete(save=True)
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = AvatarSerializer(
            user, data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=(IsAuthorOrReadOnly,)
    )
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, pk=id)

        if request.method == "POST":
            serializer = SubscriptionCreateSerializer(
                data={"user": request.user.id, "author": author.id},
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        deleted, _ = Subscription.objects.filter(
            user=request.user, author=author
        ).delete()
        if not deleted:
            raise ValidationError("Вы не подписаны на этого пользователя.")
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated],
    )
    def subscriptions(self, request):
        authors = User.objects.filter(
            subscribers__user=request.user
        ).annotate(recipes_count=Count("recipes"))
        page = self.paginate_queryset(authors)
        serializer = SubscriptionSerializer(
            page, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)
