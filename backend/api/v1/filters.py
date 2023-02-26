import django_filters
from rest_framework import filters

from recipes.models import Recipe


class RecipeFilter(django_filters.FilterSet):
    """
    Filter that only allows to get recipes.
    Filters by author, tags, adding to favorites and shopping list.
    """

    tags = django_filters.CharFilter(field_name='tags__slug')
    author = django_filters.CharFilter(
        field_name='author__username',
        lookup_expr='icontains'
        )
    is_favorited = django_filters.BooleanFilter(
        field_name='is_favorited',
        method='filter_favorite'
    )
    is_in_shopping_cart = django_filters.BooleanFilter(
        field_name='is_in_shopping_cart',
        method='filter_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'author'
        )


class IsFavoriteFilterBackend(filters.BaseFilterBackend):
    """
    Filter that only allows to get recipes added to favorites.
    """

    def filter_queryset(self, request, queryset, view):
        return queryset.django_filters(favorite__user=request.user)


class IsShoppingCartFilterBackend(filters.BaseFilterBackend):
    """
    Filter that only allows to get recipes added to shopping cart.
    """

    def filter_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(chopping_cart__user=self.request.user)
