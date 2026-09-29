from rest_framework.serializers import ModelSerializer
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


class RecipeSerializer(ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('__all__')


class TagSerializer(ModelSerializer):

    class Meta:
        model = Tag
        fields = ('__all__')


class IngredientSerializer(ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('__all__')


class FavoriteSerializer(ModelSerializer):

    class Meta:
        model = Favorite
        fields = ('__all__')


class SubscriptionSerializer(ModelSerializer):

    class Meta:
        model = Subscription
        fields = ('__all__')


class ShortLinkSerializer(ModelSerializer):

    class Meta:
        model = ShortLink
        fields = ('__all__')


class RecipeIngredientSerializer(ModelSerializer):

    class Meta:
        model = RecipeIngredient
        fields = ('__all__')


class CartSerializer(ModelSerializer):

    class Meta:
        model = Cart
        fields = ('__all__')
