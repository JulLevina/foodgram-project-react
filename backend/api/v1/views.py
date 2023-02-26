from django.db import IntegrityError
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import filters, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated
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
from api.v1.permissions import IsAuthorOrAdminOrReadOnly, AdminOrReadOnly
from api.v1.serializers import (
    IngredientWriteSerializer,
    IngredientReadSerializer,
    FavoriteSerializer,
    FollowSerializer,
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
    filter_backends = (filters.SearchFilter,)
    permission_classes = (AdminOrReadOnly,)
    search_fields = ('^name',)

    def get_serializer_class(self):
        """Defines the serializer."""
        if self.action != 'create':
            return IngredientReadSerializer
        return IngredientWriteSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """Performs all operations with recipes.
    Handles all requests for the api/v1/recipes/ endpoint."""

    queryset = Recipe.objects.all()
    http_method_names = ('get', 'post', 'patch', 'delete',)
    filter_backends = (
        filters.SearchFilter,
        DjangoFilterBackend,
        filters.OrderingFilter
    )
    filterset_class = RecipeFilter
    ordering = ('-pub_date',)

    def get_permissions(self):
        """Sets permissions."""

        if self.action in {'partial_update', 'destroy'}:
            self.permission_classes = (IsAuthorOrAdminOrReadOnly,)
        elif self.action in {'list', 'retrieve'}:
            self.permission_classes = (AllowAny,)
        return super().get_permissions()

    def get_serializer_class(self):
        """Defines the serializer."""
        if self.action in {'create', 'partial_update'}:
            return RecipeWriteSerializer
        return RecipeReadSerializer

    def get_queryset(self):
        """Returns a list of recipes."""
        return Recipe.objects.exclude(
            favorite=True).exclude(
            shoppingcart=True).select_related(
            'author').order_by('pub_date')

    def perform_create(self, serializer):
        """Saves a new instance of the author."""
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['POST', 'DELETE'])
    def favorite(self, request, pk):
        """Adds and deletes recipes to favorites.
        Handles 'POST' and 'DELETE' requests
        for the api/v1/recipes/{id}/favorites endpoint."""
        recipe = get_object_or_404(Recipe, pk=pk)
        user = self.request.user
        if self.request.method == 'POST':
            instance = Favorite.objects.create(
                    user=user,
                    recipe=recipe
                )
            serializer = FavoriteSerializer(instance)
            try:
                return Response(
                    data={
                        'Рецепт успешно добавлен в избранное': serializer.data
                    },
                    status=status.HTTP_201_CREATED
                )
            except IntegrityError:
                return Response(
                    data={'recipe': 'Данный рецепт уже добавлен в избранное'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        get_object_or_404(
            Favorite,
            recipe=recipe,
            user=self.request.user
        ).delete()
        return Response(
            {'message': 'Рецепт успешно удален из избранного'},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['POST', 'DELETE'])
    def shopping_cart(self, request, pk):
        """Adds and deletes recipes to shopping cart.
        Handles 'POST' and 'DELETE' requests
        for the api/v1/recipes/{id}/shopping cart endpoint."""
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            instance = ShoppingCart.objects.create(
                user=self.request.user,
                recipe=recipe
            )
            serializer = ShoppingCartSerializer(instance)
            try:
                return Response(
                    data={
                        'Рецепт успешно добавлен '
                        'в список покупок.': serializer.data
                    },
                    status=status.HTTP_201_CREATED
                )
            except IntegrityError:
                return Response(
                    data={
                        'recipe': 'Рецепт уже добавлен в список покупок.'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        get_object_or_404(
            ShoppingCart,
            recipe=recipe,
            user=self.request.user
        ).delete()
        return Response(
            {'message': 'Рецепт успешно удален из списка покупок'},
            status=status.HTTP_200_OK
        )

    @action(
        detail=False,
        methods=['GET'],
        url_path='download_shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """Creates a shopping cart from favorite recipes.
        Handles 'GET' request for the
        api/v1/recipes/download_shopping_cart endpoint."""
        user = self.request.user
        necessary_products = list(RecipeIngredient.objects.filter(
            recipe__shoppingcart__user=user).values(
            'ingredient__measurement_unit',
            'ingredient__name'
            ).annotate(amount=Sum('amount')
                       ).values_list(
            'ingredient__name',
            'amount',
            'ingredient__measurement_unit',
        ).order_by())
        for name, amount, unit in necessary_products:
            content = (f'{name.capitalize()}: {amount} {unit.lower()} \n')
            with open(
                'recipes/shopping_cart.txt', 'w', encoding='utf8'
            ) as shopping_cart:
                shopping_cart.write(content)
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename={0}'.format(shopping_cart)
        )
        return response


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Performs all operations with tags.
    Handles all requests for the api/v1/tags/ endpoint."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly,)


class FollowsViewSet(UserViewSet):
    """Performs all operations with follows.
    Handles all requests for the api/v1/users/sudscriptions endpoint."""

    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = (IsAuthorOrAdminOrReadOnly,)

    @action(
        methods=['GET'],
        detail=False,
        url_path='subscribtions',
        permission_classes=(IsAuthenticated,),
    )
    def subscribtions(self, request):
        """Shows user's subscriptions.
        Handles 'GET' request for
        the api/v1/users/subscribtions endpoint."""
        queryset = Follows.objects.filter(user=request.user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(pages, many=True)
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['POST', 'DELETE'],
        detail=True, url_path='subscribe',
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, **kwargs):
        """Create user's subscriptions.
        Handles 'POST', 'DELETE' requests for
        the api/v1/users/{id}/subscribe endpoint."""
        author = get_object_or_404(User, pk=self.kwargs['id'])
        if request.method == 'POST':
            instance = Follows.objects.create(
                user=self.request.user,
                author=author
            )
            serializer = FollowSerializer(instance)
            try:
                return Response(
                    data={'Подписка успешно создана': serializer.data},
                    status=status.HTTP_201_CREATED
                )
            except IntegrityError:
                return Response(
                    data={
                        'recipe': 'Вы уже подписаны на данного пользователя.'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        get_object_or_404(
            Follows,
            user=self.request.user,
            author=author
        ).delete()
        return Response(
            {'message': 'Подписка успешно удалена'},
            status=status.HTTP_200_OK
        )
