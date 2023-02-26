from rest_framework.routers import DefaultRouter
from django.urls import path, re_path, include

from .views import (
    IngredientViewSet,
    FollowsViewSet,
    RecipeViewSet,
    TagViewSet,
)

v1_router = DefaultRouter()

v1_router.register('recipes', RecipeViewSet, basename='recipes')
v1_router.register('ingredients', IngredientViewSet, basename='ingredients')
v1_router.register('tags', TagViewSet, basename='tags')
v1_router.register('users', FollowsViewSet, basename='users')

urlpatterns = [
    path('', include(v1_router.urls)),
    re_path(r'^auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken'))
]
