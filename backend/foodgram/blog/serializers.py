from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField
from users.tools import Base64ImageField
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
    image = Base64ImageField(required=True)
    author = PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'name', 'image', 'text', 'cooking_time', 'tags', 'ingredient',)


class TagSerializer(ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug',)


class IngredientSerializer(ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


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
