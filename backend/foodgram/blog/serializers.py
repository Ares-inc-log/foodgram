from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField
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
from users.serializers import MyUserSerializer


class TagSerializer(ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug',)


class RecipeIngredientReadSerializer(ModelSerializer):
    id = PrimaryKeyRelatedField(source='ingredient.id', read_only=True)
    name = PrimaryKeyRelatedField(source='ingredient.name', read_only=True)
    measurement_unit = PrimaryKeyRelatedField(source='ingredient.measurement_unit', read_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

class RecipeIngredientWriteSerializer(ModelSerializer):
    id = PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeWriteSerializer(ModelSerializer):
    tags = PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = RecipeIngredientWriteSerializer(many=True, write_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'text',
            'cooking_time',
            'tags',
            'ingredients',
        )

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        tags_data = validated_data.pop('tags', None)
        
        instance = super().update(instance, validated_data)
        
        if tags_data is not None:
            instance.tags.set(tags_data)
            
        if ingredients_data is not None:
            RecipeIngredient.objects.filter(recipe=instance).delete()
            RecipeIngredient.objects.bulk_create([
                RecipeIngredient(
                    recipe=instance,
                    ingredient=ingredient_data['id'],
                    amount=ingredient_data['amount']
                ) for ingredient_data in ingredients_data
            ])
            
        return instance


class RecipeReadSerializer(ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = MyUserSerializer(read_only=True)
    ingredients = RecipeIngredientReadSerializer(many=True, source='recipe_ingredients', read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'name',
            'image',
            'text',
            'cooking_time',
            'tags',
            'ingredients',
        )


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
