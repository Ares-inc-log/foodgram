from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    ActivateUserView,
    AccountViewSet,
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
    redirect_short_link,
)

router = DefaultRouter()
router.register("users", AccountViewSet, basename="users")
router.register("recipes", RecipeViewSet, basename="recipes")
router.register("tags", TagViewSet, basename="tags")
router.register("ingredients", IngredientViewSet, basename="ingredients")

urlpatterns = [
    path("api/activate/<str:uid>/<str:token>/", ActivateUserView.as_view()),
    path("api/auth/", include("djoser.urls.authtoken")),
    path("api/", include(router.urls)),
    path("s/<str:short_link>/", redirect_short_link, name="short-link"),
]
