from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    CustomUserViewSet,
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
    short_link_redirect,
)

router = DefaultRouter()

router.register("users", CustomUserViewSet, basename="users")
router.register("recipes", RecipeViewSet, basename="recipes")
router.register("tags", TagViewSet, basename="tags")
router.register("ingredients", IngredientViewSet, basename="ingredients")


urlpatterns = [
    path("api/", include(router.urls)),
    path("s/<int:pk>/", short_link_redirect, name="short-link"),
]
