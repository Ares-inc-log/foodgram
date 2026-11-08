from django.contrib import admin
from django.db.models import Count

from blog.models import Ingredient, Recipe, RecipeIngredient, Tag


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    min_num = 1


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "measurement_unit",
    )
    search_fields = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
    )


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "author",
        "name",
    )
    search_fields = (
        "author",
        "name",
    )
    list_filter = ("tags",)
    inlines = [RecipeIngredientInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(favorites_count=Count("favorited_by"))

    @admin.display(description="В избранном", ordering="favorites_count")
    def favorites_count(self, obj):
        return obj.favorites_count

    @admin.display(description="В избранном")
    def favorites_count_display(self, obj):
        return obj.favorited_by.count()
