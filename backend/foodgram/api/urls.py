from django.urls import include, path
from rest_framework.routers import DefaultRouter, SimpleRouter
from api.views import (
    CustomUserViewSet,
    TagViewSet,
    RecipeViewSet,
    IngredientViewSet
)


router = DefaultRouter()

router.register('users', CustomUserViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet, basename='ingredients')


urlpatterns = [
    path('api/', include(router.urls)),
]