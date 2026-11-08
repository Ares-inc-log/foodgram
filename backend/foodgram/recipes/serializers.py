from django.contrib.gis import serializers
from django.db import transaction
from rest_framework.serializers import (
    CharField,
    ModelSerializer,
    PrimaryKeyRelatedField,
    SerializerMethodField,
)
from users.tools import Base64ImageField
from api.serializers import AccountSerializer

from recipes.models import (
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

    class Meta:
        model = RecipeIngredient
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount",
        )
        read_only_fields = ("measurement_unit")


class RecipeIngredientWriteSerializer(ModelSerializer):
    id = PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredient
        fields = ("id", "amount")

    def validate_ingredients(self, value):
        ids = []
        for item in value:
            ids.append(item["id"])
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError(
                "Ингредиенты не должны повторяться."
            )
        return value


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
        tags = validated_data["tags"]
        ingredients_data = validated_data["ingredients"]
        recipe_fields = {
            key: value
            for key, value in validated_data.items()
            if key not in ("tags", "ingredients")
        }
        recipe = Recipe.objects.create(**recipe_fields)
        recipe.tags.set(tags)
        self._save_ingredients(recipe, ingredients_data)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = validated_data.get("tags")
        ingredients_data = validated_data.get("ingredients")
        recipe_fields = {
            key: value
            for key, value in validated_data.items()
            if key not in ("tags", "ingredients")
        }
        for field, value in recipe_fields.items():
            setattr(instance, field, value)
        instance.save()
        if tags is not None:
            instance.tags.set(tags)
        if ingredients_data is not None:
            instance.recipe_ingredients.all().delete()
            self._save_ingredients(instance, ingredients_data)
        return instance

    def _save_ingredients(self, recipe, ingredients_data):
        recipe_ingredients = []
        for item in ingredients_data:
            recipe_ingredients.append(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=item["id"],
                    amount=item["amount"],
                )
            )
        RecipeIngredient.objects.bulk_create(recipe_ingredients)


class RecipeReadSerializer(ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = AccountSerializer(read_only=True)
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
