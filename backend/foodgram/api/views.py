from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
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


User = get_user_model()


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


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
