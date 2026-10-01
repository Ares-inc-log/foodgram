from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from djoser.views import UserViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
    AllowAny
)
from blog.models import (
    Recipe,
    Tag,
    Ingredient,
    ShortLink,
    RecipeIngredient,
    Favorite,
    Cart,
    Subscription
)
from blog.serializers import (
    RecipeSerializer,
    TagSerializer,
    IngredientSerializer,
    RecipeIngredientSerializer,
    FavoriteSerializer,
    CartSerializer,
    ShortLinkSerializer,
    SubscriptionSerializer
)
from users.serializers import AvatarSerializer


User = get_user_model()


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (AllowAny,)

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        name_param = self.request.query_params.get('name')
        
        if name_param:
            queryset = queryset.filter(name__istartswith=name_param)
            
        return queryset


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (AllowAny,)


class CartViewSet(ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = (IsAuthenticated,)


class SubscriptionbViewSet(ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = (IsAuthenticated,)


class ShortLinkbViewSet(ModelViewSet):
    queryset = ShortLink.objects.all()
    serializer_class = ShortLinkSerializer


class FavoriteViewSet(ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = (IsAuthenticated,)


class RecipeIngredientViewSet(ModelViewSet):
    queryset = RecipeIngredient.objects.all()
    serializer_class = RecipeIngredientSerializer


class CustomUserViewSet(UserViewSet):

    @action(
        detail=False,
        methods=['get', 'put', 'delete'],
        url_path='me/avatar',
        permission_classes=[IsAuthenticated],
    )
    def avatar(self, request):
        user = request.user
        if request.method == 'DELETE':
            user.avatar.delete(save=True)
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = AvatarSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)