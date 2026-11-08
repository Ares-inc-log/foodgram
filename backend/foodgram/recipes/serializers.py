from django.db import transaction
from rest_framework.serializers import (
    CharField,
    ModelSerializer,
    PrimaryKeyRelatedField,
    SerializerMethodField,
)
from users.serializers import MyUserSerializer
from users.tools import Base64ImageField

from blog.models import (
    Ingredient,
    Recipe,
    RecipeIngredient,
    Tag,
)


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            "id",
            "name",
            "slug",
        )


class RecipeIngredientReadSerializer(ModelSerializer):
    id = PrimaryKeyRelatedField(source="ingredient.id", read_only=True)
    name = PrimaryKeyRelatedField(source="ingredient.name", read_only=True)
    measurement_unit = PrimaryKeyRelatedField(
        source="ingredient.measurement_unit", read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount",
        )


class RecipeIngredientWriteSerializer(ModelSerializer):
    id = PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredient
        fields = ("id", "amount")


class RecipeWriteSerializer(ModelSerializer):
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    ingredients = RecipeIngredientWriteSerializer(many=True, write_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "text",
            "cooking_time",
            "tags",
            "ingredients",
        )

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop("tags")
        ingredients_data = validated_data.pop("ingredients")

        recipe = Recipe.objects.create(**validated_data)

        recipe.tags.set(tags)

        recipe_ingredients = [
            RecipeIngredient(
                recipe=recipe, ingredient=item["id"], amount=item["amount"]
            )
            for item in ingredients_data
        ]
        RecipeIngredient.objects.bulk_create(recipe_ingredients)

        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop("tags", None)
        ingredients_data = validated_data.pop("ingredients", None)

        instance = super().update(instance, validated_data)

        if tags is not None:
            instance.tags.set(tags)

        if ingredients_data is not None:
            RecipeIngredient.objects.filter(recipe=instance).delete()

            recipe_ingredients = [
                RecipeIngredient(
                    recipe=instance,
                    ingredient=item["id"],
                    amount=item["amount"],
                )
                for item in ingredients_data
            ]
            RecipeIngredient.objects.bulk_create(recipe_ingredients)

        return instance


class RecipeReadSerializer(ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = MyUserSerializer(read_only=True)
    ingredients = RecipeIngredientReadSerializer(
        many=True, source="recipe_ingredients", read_only=True
    )
    source_link = CharField(source="short_link", read_only=True)
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "author",
            "name",
            "image",
            "text",
            "cooking_time",
            "tags",
            "ingredients",
            "source_link",
            "is_favorited",
            "is_in_shopping_cart",
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["short-link"] = representation.pop("source_link")
        return representation

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        return bool(
            request
            and request.user.is_authenticated
            and obj.favorites.filter(user=request.user).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        return bool(
            request
            and request.user.is_authenticated
            and obj.shopping_carts.filter(user=request.user).exists()
        )


class RecipeShortSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")
        read_only_fields = fields


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "slug")
