from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import filters, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny,
)
from rest_framework.response import Response

from recipes.models import (
    Ingredient,
    Favorite,
    Follows,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag
)
from users.models import User
from api.v1.serializers import (
    DownloadShoppinCartSerializer,
    IngredientWriteSerializer,
    IngredientReadSerializer,
    FavoriteSerializer,
    FollowSerializer,
    FollowsUserSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    ShoppingCartSerializer,
    TagSerializer,
    UserCreateSerializer
)
from api.v1.filters import RecipeFilter


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Performs all operations with ingredients.
    Handles all requests for the api/v1/ingreients/ endpoint."""

    queryset = Ingredient.objects.order_by('name')

    def get_serializer_class(self):
        if self.action != 'create':
            return IngredientReadSerializer
        return IngredientWriteSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """Performs all operations with recipes.
    Handles all requests for the api/v1/recipes/ endpoint."""

    queryset = Recipe.objects.all()
    http_method_names = ('get', 'post', 'patch', 'delete',)
    permission_classes = (AllowAny,)
    filter_backends = (filters.SearchFilter,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in {'create', 'partial_update'}:
            return RecipeWriteSerializer
        return RecipeReadSerializer
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    
    @action(detail=True, methods=['POST', 'DELETE'])
    def favorite(self, request, pk):
        """Adds and deletes recipes to favorites.
        Handles 'POST' and 'DELETE' requests
        for the api/v1/recipes/{id}/favorites endpoint."""
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            instance = Favorite.objects.create(user=self.request.user, recipe=recipe)
            serializer = FavoriteSerializer(instance) #serializer = FavoriteSerializer(instance)
            # if serializer.is_valid():
            #     serializer.save()
            return Response(data={"Рецепт успешно добавлен в избранное": serializer.data}, status=status.HTTP_201_CREATED)
            #return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        get_object_or_404(Favorite, recipe=recipe, user=self.request.user).delete()
        return Response({"message": "Рецепт успешно удален из избранного"}, status=status.HTTP_200_OK)


    @action(detail=True, methods=['POST', 'DELETE'])
    def shopping_cart(self, request, pk):
        """Adds and deletes recipes to shopping_cart.
        Handles 'POST' and 'DELETE' requests
        for the api/v1/recipes/{id}/shopping_cart endpoint."""
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            instance = ShoppingCart.objects.create(user=self.request.user, recipe=recipe)
            serializer = ShoppingCartSerializer(instance)
            return Response(data={"Рецепт успешно добавлен в список покупок": serializer.data}, status=status.HTTP_201_CREATED)
        get_object_or_404(ShoppingCart, recipe=recipe, user=self.request.user).delete()
        return Response({"message": "Рецепт успешно удален из списка покупок"}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['GET'], url_path='download_shopping_cart')
    def download_shopping_cart(self, request, **kwargs):
        """Creates a shopping_cart from favorite recipes.
        Handles 'GET' request for the api/v1/recipes/download_shopping_cart endpoint."""
        user = self.request.user
        instance = RecipeIngredient.objects.filter(recipe__shoppingcart__user=user).values(
            'ingredient__measurement_unit',
            'ingredient__name', 
            #'ingredient__recipeingredient__amount'
            )
        #recipe_id = get_object_or_404(Recipe, pk=self.kwargs['recipe_id'])
        # recipes = ShoppingCart.objects.all()
        # for recipe in recipes:
        #     recipe = get_object_or_404(ShoppingCart, pk=pk)
        #data = RecipeIngredient.objects.filter(recipe_id=3).select_related('recipe', 'ingredient')
        serializer = DownloadShoppinCartSerializer(instance, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
        
        # recipe = get_object_or_404(ShoppingCart, pk=self.kwargs['recipe_id'])
        # instance = Recipe.objects.get(recipe.ingredients)
        # serializer = DownloadShoppinCartSerializer(instance, many=True)
        # return Response(data=serializer.data, status=status.HTTP_200_OK)



class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Performs all operations with tags.
    Handles all requests for the api/v1/tags/ endpoint."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
        

class FollowsViewSet(UserViewSet):
    """Performs all operations with follows.
    Handles all requests for the api/v1/users/sudscriptions endpoint."""
    
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = (AllowAny,)
    

    @action(methods=['GET'], detail=False, url_path='subscriptions')
    def subscribtions(self, request):
        """Shows user's subscriptions.
        Handles 'GET' request for the api/v1/users/subscribtions endpoint."""
        instance = Follows.objects.filter(author__following__user=request.user)
        serializer = FollowSerializer(instance, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(methods=['POST', 'DELETE'], detail=True, url_path='subscribe')
    def subscribe(self, request, **kwargs):
        """Create user's subscriptions.
        Handles 'POST', 'DELETE' requests for the api/v1/users/{id}/subscribe endpoint."""
        author = get_object_or_404(User, pk=self.kwargs['id'])
        if request.method == 'POST':
            instance = Follows.objects.create(user=self.request.user, author=author)
            serializer = FollowSerializer(instance)
            return Response(data={"Подписка успешно создана": serializer.data}, status=status.HTTP_201_CREATED)
        get_object_or_404(Follows, author=author, user=self.request.user).delete()
        return Response({"message": "Подписка успешно удалена"}, status=status.HTTP_200_OK)
