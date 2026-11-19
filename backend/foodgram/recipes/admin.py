from django.contrib import admin
from django.db.models import Count

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    min_num = 1


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit")
    search_fields = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("name", "author", "favorites_count")
    search_fields = ("name", "author__username")
    list_filter = ("tags",)
    list_select_related = ("author",)
    inlines = (RecipeIngredientInline,)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            favorites_total=Count("favorites")
        )

    @admin.display(description="В избранном", ordering="favorites_total")
    def favorites_count(self, obj):
        return obj.favorites_total


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ("recipe", "ingredient", "amount")
    search_fields = ("recipe__name", "ingredient__name")
    list_select_related = ("recipe", "ingredient")


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe")
    search_fields = ("user__username", "recipe__name")
    list_select_related = ("user", "recipe")


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe")
    search_fields = ("user__username", "recipe__name")
    list_select_related = ("user", "recipe")
