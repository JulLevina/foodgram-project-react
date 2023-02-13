from rest_framework.routers import DefaultRouter
from django.urls import path, re_path, include
from djoser.views import UserViewSet

from .views import (
    IngredientViewSet,
    #CustomUserCreateViewSet,
    is_favorite,
    RecipeViewSet,
    FollowViewSet,
    TagViewSet,
    #UserViewSet
)

v1_router = DefaultRouter()

v1_router.register('recipes', RecipeViewSet, basename='recipes')
v1_router.register('ingredients', IngredientViewSet, basename='ingredients')
v1_router.register('tags', TagViewSet, basename='tags')
#v1_router.register(r'recipes/(?P<recipe_id>\d+)/favorites', is_favorite, basename='favorites')
v1_router.register('users', UserViewSet, basename='users')
#v1_router.register('users/subscribtions', SubscribeViewSet, basename='subscribe')
v1_router.register(r'users/(?P<user_id>\d+)/subscribe', FollowViewSet, basename='subscribe')

#url_favorites = [path('recipes/<int:pk>/favorites', is_favorite),
#]

urlpatterns = [
    #path('url_favorites', include(url_favorites)),
    path('', include(v1_router.urls)),
    # re_path(r'^token/login/?$', views.TokenCreateView.as_view(), name='login'),
    # re_path(r'^token/logout/?$', views.TokenDestroyView.as_view(), name='logout'),
    re_path(r'^auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken'))

]