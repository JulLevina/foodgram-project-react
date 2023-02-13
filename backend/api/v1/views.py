from rest_framework import mixins, viewsets, generics
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import (
    AllowAny,)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from recipes.models import Ingredient, Favorite, Follows, Recipe, Tag, User
from api.v1.serializers import (
    UserCreateSerializer,
    IngredientSerializer,
    #FavoriteSerializer,
    FollowSerializer,
    RecipeIngredientSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    TagSerializer,
    #UserSerializer
)

class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Performs all operations with ingredients.
    Handles all requests for the api/v1/ingreients/ endpoint."""

    queryset = Ingredient.objects.all() # order_by('name')
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """Performs all operations with recipes.
    Handles all requests for the api/v1/recipes/ endpoint."""

    queryset = Recipe.objects.all()
    http_method_names = ('get', 'post', 'patch', 'delete',)

    def get_serializer_class(self):
        if self.action in {'create', 'partial_update'}:
            return RecipeWriteSerializer
        return RecipeReadSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Performs all operations with tags.
    Handles all requests for the api/v1/tags/ endpoint."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


@api_view(['POST', 'DELETE'])
@permission_classes((AllowAny,))
def is_favorite(request, pk):
    """Performs all operations with favorites.
    Handles all requests for the api/v1/recipes/{id}/favorites endpoint."""

    # favorite_recipe = Favorite.objects.get(pk=pk)
    # if request.method == 'POST':
    #     return Response({"message": "Рецепт успешно добавлен в ихбранное", "data": request.data})
    # favorite_recipe.delete()
    # return Response({"message": "Рецепт успешно удален из избранного"})
    

class FollowViewSet(viewsets.ModelViewSet):
    serializer_class = FollowSerializer
    queryset = Follows.objects.all()

    @action(detail=False)
    def subscriptions(self, request):
        followings = User.objects.all()
        # Передадим queryset cats сериализатору 
        # и разрешим работу со списком объектов
        serializer = self.get_serializer(followings, many=True)
        return Response(serializer.data) 

    # def follows(self, request):
    #     follows = Follows.objects.filter(following__user=user)
    #     serialiser = ...
        

# class CustomUserCreateViewSet(UserViewSet):
#     queryset = User.objects.all()
#     serializer_class = CustomUserCreateSerializer

    # def get_queryset(self):
    #     queryset = User.objects.all()
    #     user_id = self.request.user.id
    #     # Через ORM отфильтровать объекты модели Cat
    #     # по значению параметра color, полученного в запросе
    #     queryset = queryset.filter(pk=user_id)
    #     return queryset 

# class UserViewSet(viewsets.ModelViewSet):

#     queryset = User.objects.all()
#     serializer_class = UserCreateSerializer

#     @action(detail=False, methods=['get'])
#     def me(self, request):
#         user = User.objects.filter(pk=request.user.id)
#         serializer = self.get_serializer(user)
#         return Response(serializer.data)
