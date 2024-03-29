import io

from django.db.models import Count, Exists, OuterRef, Sum
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.serializers import SetPasswordSerializer
from rest_framework import filters, mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.v1.filters import RecipeFilter
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
from recipes.models import (
    Ingredient,
    Favorite,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag
)
from users.models import Subscription, User


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
        if self.action == 'create':
            self.permission_classes = (IsAuthenticated,)
        elif self.action in {'partial_update', 'destroy'}:
            self.permission_classes = (IsAuthorOrReadOnly,)
        return super().get_permissions()

    def get_serializer_class(self):
        """Определяет сериализатор."""
        if self.action in {'create', 'partial_update', 'destroy'}:
            return recipes.RecipeWriteSerializer
        if self.action == 'favorite':
            return favorites.FavoriteSerializer
        if self.action == 'shopping_cart':
            return shopping_cart.ShoppingCartSerializer
        return recipes.RecipeReadSerializer

    def get_queryset(self):
        """Возвращает список рецептов."""
        user_id = self.request.user.id or None
        return Recipe.objects.select_related('author').prefetch_related(
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
            ))

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
    def creating_favorites_or_cart(serializer_class):
        serializer_class.is_valid(raise_exception=True)
        serializer_class.save()
        return Response(serializer_class.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['POST', ])
    def favorite(self, request, pk):
        """Добавляет рецепты в избранное.
        Обрабатывает 'POST' запросы для эндпоинта
        api/v1/recipes/{id}/favorites."""
        return self.creating_favorites_or_cart(self.get_serializer(
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
            self.get_serializer(
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
                'ingredient__name').annotate(
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


class UserSubscriptionViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """Выполняет все операции с пользователями.
    Обрабатывает все запросы для эндпоинта
    api/v1/users/subscriptions."""

    queryset = User.objects.all()

    def get_permissions(self):
        """Устанавливает разрешения."""
        if self.action in {'create', 'list'}:
            self.permission_classes = (AllowAny,)
        elif self.action in {'retrieve', 'me', 'set_password'}:
            self.permission_classes = (IsAuthenticated,)
        return super().get_permissions()

    def get_serializer_class(self):
        """Определяет сериализатор."""
        if self.action == 'subscriptions':
            return subscribtions.FollowSerializer
        if self.action == 'subscribe':
            return subscribtions.SubscribeSerializer
        if self.action in {'list', 'retrieve', 'me'}:
            return users.UserSerializer
        if self.action == 'set_password':
            return SetPasswordSerializer
        return users.UserCreateSerializer

    def get_queryset(self):
        user_id = self.request.user.id or None
        if self.action in {'subscriptions', 'subscribe'}:
            return Subscription.objects.filter(
                user=self.request.user
            ).annotate(
                recipes_count=Count('author__recipes'),)
        return User.objects.annotate(
            is_subscribed=Exists(
                Subscription.objects.filter(
                    author_id=OuterRef('id'),
                    user=user_id
                )
            )
        ).prefetch_related('subscribers', 'authors')

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
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(
                page,
                many=True,
                context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(
        methods=['POST'],
        detail=True, url_path='subscribe',
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, pk=None):
        """Создает подписку на пользователя.
        Обрабатывает 'POST' запросы для
        эндпоинта api/v1/users/{id}/subscribe."""
        serializer = self.get_serializer(
            data={'author': pk},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, pk):
        """Удаляет подписку.
        Обрабатывает 'DELETE' запросы для эндпоинта
        api/v1/recipes/{id}/subscriptions."""
        get_object_or_404(
            Subscription,
            author_id=pk,
            user=request.user
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
