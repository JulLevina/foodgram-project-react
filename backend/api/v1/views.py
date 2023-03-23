import io

from django.db.models import Count, Exists, OuterRef, Sum, Value
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import filters, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from recipes.models import (
    Ingredient,
    Favorite,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag
)
from users.models import Subscription, User
from api.v1.permissions import IsAuthorOrReadOnly
from api.v1.serializers import (
    ingredients,
    favorites,
    recipes,
    shopping_cart,
    subscribtions,
    tags,
    users
)
from api.v1.filters import RecipeFilter


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Выполняет все операции с ингредиентами.
    Обрабатывает все запросы для эндпоинта api/v1/ingreients/."""

    queryset = Ingredient.objects.order_by('name')
    serializer_class = ingredients.IngredientReadSerializer
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """Выполняет все операции с зецептами.
    Обрабатывает все запросы для эндпоинта api/v1/recipes/."""

    queryset = Recipe.objects.all()
    http_method_names = ('get', 'post', 'patch', 'delete',)
    filter_backends = (
        DjangoFilterBackend,
    )
    filterset_class = RecipeFilter

    def get_permissions(self):
        """Устанавливает разрешения."""
        if self.action in {'create', 'retrieve'}:
            self.permission_classes = (IsAuthenticated,)
        elif self.action in {'partial_update', 'destroy'}:
            self.permission_classes = (IsAuthorOrReadOnly,)
        elif self.action == 'list':
            self.permission_classes = (AllowAny,)
        return super().get_permissions()

    def get_serializer_class(self):
        """Определяет сериализатор."""
        if self.action in {'create', 'partial_update', 'destroy'}:
            return recipes.RecipeWriteSerializer
        return recipes.RecipeReadSerializer

    def get_queryset(self):
        """Возвращает список рецептов."""
        user_id = self.request.user.id or None
        return Recipe.objects.annotate(
            is_favorited=Value(False),
            is_in_shopping_cart=Value(False)
            ).select_related('author').prefetch_related(
            'recipes', 'tags', 'ingredients', 'favorites'
        ).annotate(
            is_favorited=Exists(
                Favorite.objects.filter(
                    recipe_id=OuterRef('id'),
                    user=user_id
                )
            ),
            is_in_shopping_cart=Exists(
                ShoppingCart.objects.filter(
                    recipe=OuterRef('id'),
                    user=user_id
                )
            )).select_related('author').prefetch_related(
                'recipes', 'tags', 'ingredients', 'favorites'
        )

    def perform_create(self, serializer):
        """Сохраняет новое значение для автора."""
        serializer.save(author=self.request.user)

    @staticmethod
    def delete_method(model, request, pk):
        user_id = request.user.id or None
        get_object_or_404(
            model,
            recipe_id=pk,
            user=user_id
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def creating_favorites_or_cart(serializer):
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['POST', ])
    def favorite(self, request, pk):
        """Добавляет рецепты в избранное.
        Обрабатывает 'POST' запросы для эндпоинта
        api/v1/recipes/{id}/favorites."""
        return self.creating_favorites_or_cart(favorites.FavoriteSerializer(
            data={'recipe': pk},
            context={'request': request}
        ))

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        """Удаляет рецепт из избранного.
        Обрабатывает 'DELETE' запросы для эндпоинта
        api/v1/recipes/{id}/favorites."""
        return self.delete_method(request=request, pk=pk, model=Favorite)

    @action(
        detail=True,
        methods=['POST', ],
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        """Добавляет рецепты в список покупок.
        Обрабатывает 'POST' запросы для эндпоинта
        api/v1/recipes/{id}/shopping cart."""
        return self.creating_favorites_or_cart(
            shopping_cart.ShoppingCartSerializer(
                data={'recipe': pk},
                context={'request': request}
            )
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        """Удаляет рецепт из списка покупок.
        Обрабатывает 'DELETE' запросы для эндпоинта
        api/v1/recipes/{id}/shopping cart."""
        return self.delete_method(request=request, pk=pk, model=ShoppingCart)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """Создает список покупок для скачивания.
        Обрабатывает 'GET' запросы для эндпоинта
        api/v1/recipes/download_shopping_cart."""
        user = self.request.user
        necessary_products = RecipeIngredient.objects.filter(
            recipe__shoppingcart__user=user).values(
                'ingredient__measurement_unit',
                'ingredient__name'
                ).annotate(
                    total=Sum('amount')
                ).order_by('recipe').order_by('ingredient__name')
        content = '\n'.join([
            f'{ingredient["ingredient__name"].capitalize()}: '
            f'{ingredient["total"]} '
            f'{ingredient["ingredient__measurement_unit"].lower()}'
            for ingredient in necessary_products
        ])
        shopping_cart = io.StringIO()
        shopping_cart.write(content)
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename={0}'.format(shopping_cart)
        )
        return response


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Выполняет все операции с тэгами.
    Обрабатывает запросы для эндпоинта the api/v1/tags/."""

    queryset = Tag.objects.all()
    serializer_class = tags.TagSerializer
    pagination_class = None


class UserSubscriptionViewSet(UserViewSet):
    """Выполняет все операции с пользователями.
    Обрабатывает все запросы для эндпоинта
    api/v1/users/sudscriptions."""

    queryset = User.objects.all()
    http_method_names = ('get', 'post', 'delete')

    def get_permissions(self):
        """Устанавливает разрешения."""
        if self.action in {'create', 'list'}:
            self.permission_classes = (AllowAny,)
        elif self.action == 'retrieve':
            self.permission_classes = (IsAuthenticated,)
        return super().get_permissions()

    def get_serializer_class(self):
        """Определяет сериализатор."""
        if self.action in {'subscriptions', 'subscribe', 'destroy'}:
            return subscribtions.FollowSerializer
        return users.UserSerializer

    def get_queryset(self):
        if self.action in {'subscriptions', 'subscribe'}:
            return Subscription.objects.filter(
                user=self.request.user
                    ).annotate(
                        recipes_count=Count('author__recipe_set'),)
        return User.objects.all()

    @action(
        detail=False,
        url_path='subscriptions',
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        """Возвращает список подписок пользователя.
        Обрабатывает 'GET' запросы для эндпоинта
        api/v1/users/subscribtions."""
        queryset = self.get_queryset()
        # Subscription.objects.filter(user=request.user).annotate(
        #     recipes_count=Count('author__recipe_set'),)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(
        methods=['POST', ],
        detail=True, url_path='subscribe',
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, **kwargs):
        """Создает подписку на пользователя.
        Обрабатывает 'POST' запросы для
        эндпоинта api/v1/users/{id}/subscribe."""
        serializer = subscribtions.FollowSerializer(
                data={'author': self.kwargs['id']},
                context={'request': request}
            )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, **kwargs):
        """Удаляет подписку.
        Обрабатывает 'DELETE' запросы для эндпоинта
        api/v1/recipes/{id}/subscriptions."""
        get_object_or_404(
            Subscription,
            author_id=self.kwargs['id'],
            user=request.user
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
