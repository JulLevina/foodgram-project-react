from rest_framework.routers import DefaultRouter
from django.urls import path, include
from djoser.views import UserViewSet

from .views import (
    IngredientViewSet,
    UserSubscriptionViewSet,
    RecipeViewSet,
    TagViewSet,
)

v1_router = DefaultRouter()

v1_router.register('recipes', RecipeViewSet, basename='recipes')
v1_router.register('ingredients', IngredientViewSet, basename='ingredients')
v1_router.register('tags', TagViewSet, basename='tags')
v1_router.register('users', UserSubscriptionViewSet, basename='users')

urlpatterns = [
    path('users/set_password/', UserViewSet.as_view(
        {'post': 'set_password'}
    ), name='set_password'),
    path('users/me/', UserViewSet.as_view({'get': 'me'}), name='me'),
    path('', include(v1_router.urls)),
    path('auth/', include('djoser.urls.authtoken'))
]
