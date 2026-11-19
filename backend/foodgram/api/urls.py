from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    AccountViewSet,
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
)

router = DefaultRouter()
router.register("users", AccountViewSet, basename="users")
router.register("recipes", RecipeViewSet, basename="recipes")
router.register("tags", TagViewSet, basename="tags")
router.register("ingredients", IngredientViewSet, basename="ingredients")


urlpatterns = [
    path("api/", include(router.urls)),
    path("api/auth/", include("djoser.urls.authtoken")),
]
