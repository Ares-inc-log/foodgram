from django.contrib.auth import get_user_model
from django.db import transaction
from djoser.serializers import UserSerializer
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from rest_framework import serializers
from rest_framework.serializers import (
    CharField,
    ModelSerializer,
    PrimaryKeyRelatedField,
    SerializerMethodField,
)
from rest_framework.validators import UniqueTogetherValidator
from users.tools import Base64ImageField

User = get_user_model()


class AccountSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = (
            "id", "email", "username", "first_name", "last_name",
            "is_subscribed", "avatar",
        )

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        return False


class AvatarSerializer(ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ("avatar",)


class TagSerializer(ModelSerializer):

    class Meta:
        model = Tag
        fields = (
            "id",
            "name",
            "slug",
        )


class RecipeIngredientReadSerializer(ModelSerializer):
    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount",)


class RecipeIngredientWriteSerializer(ModelSerializer):
    id = PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredient
        fields = ("id", "amount",)

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                "Список ингредиентов не может быть пустым."
            )
        ids = [item["id"] for item in value]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError(
                "Ингредиенты не должны повторяться."
            )
        return value


class RecipeWriteSerializer(ModelSerializer):
    tags = PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, allow_empty=False
    )
    ingredients = RecipeIngredientWriteSerializer(
        many=True, write_only=True, allow_empty=False
    )
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

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
            "is_favorited",
            "is_in_shopping_cart",
        )

    def validate(self, attrs):
        ingredients = attrs.get("ingredients")
        tags = attrs.get("tags")
        cooking_time = attrs.get("cooking_time")

        if not ingredients:
            raise serializers.ValidationError(
                {"ingredients": "Нужно указать хотя бы один ингредиент."}
            )
        ids = [item["id"] for item in ingredients]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError(
                {"ingredients": "Ингредиенты не должны повторяться."}
            )

        if not tags:
            raise serializers.ValidationError(
                {"tags": "Нужно указать хотя бы один тег."}
            )
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                {"tags": "Теги не должны повторяться."}
            )

        if not cooking_time:
            raise serializers.ValidationError(
                {"cooking_time": "Время приготовления должно быть указано."}
            )
        return attrs

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

    def _is_related(self, obj, related_name):
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        return getattr(obj, related_name).filter(user=request.user).exists()

    def get_is_favorited(self, obj):
        return self._is_related(obj, "favorites")

    def get_is_in_shopping_cart(self, obj):
        return self._is_related(obj, "shopping_carts")


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
        fields = ("id", "name", "image", "cooking_time",)
        read_only_fields = fields


class IngredientSerializer(ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit",)


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Favorite
        fields = ("user", "recipe",)
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=("user", "recipe"),
                message="Рецепт уже в избранном",
            )
        ]

    def to_representation(self, instance):
        serializer = RecipeShortSerializer(
            instance.recipe, context=self.context
        )
        return serializer.data


class ShoppingCartSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = ShoppingCart
        fields = ("user", "recipe",)
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=("user", "recipe",),
                message="Рецепт уже в списке покупок",
            )
        ]

    def to_representation(self, instance):
        serializer = RecipeShortSerializer(
            instance.recipe, context=self.context
        )
        return serializer.data


class SubscriptionSerializer(AccountSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source="recipes.count", read_only=True
    )

    class Meta(AccountSerializer.Meta):
        fields = AccountSerializer.Meta.fields + ("recipes", "recipes_count")

    def get_recipes(self, obj):
        request = self.context.get("request")
        recipes = obj.recipes.all()
        limit = request.query_params.get("recipes_limit") if request else None
        if limit and limit.isdigit():
            recipes = recipes[: int(limit)]
        return RecipeShortSerializer(
            recipes, many=True, context=self.context
        ).data
