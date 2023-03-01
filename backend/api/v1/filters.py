import django_filters
from rest_framework import filters

from recipes.models import Ingredient, Recipe


class IngredientFilter(django_filters.FilterSet):
    """Фильтрация списка ингредиентов по названию."""

    name = django_filters.CharFilter(
        field_name='name', lookup_expr='startswith'
    )

    class Meta:
        model = Ingredient
        fields = ['name']


class RecipeFilter(django_filters.FilterSet):
    """
    Фильтрация рецептов по автору, добавлению в избранное и список покупок.
    """

    tags = django_filters.CharFilter(field_name='tags__slug')
    author = django_filters.CharFilter(
        field_name='author__username',
        lookup_expr='icontains'
        )
    is_favorited = django_filters.BooleanFilter(
        field_name='is_favorited',
        method='unchecked_means_any_value'
    )
    is_in_shopping_cart = django_filters.BooleanFilter(
        field_name='is_in_shopping_cart',
        method='unchecked_means_any_value'
    )

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'author',
            'is_favorited',
            'is_in_shopping_cart'
        )

    def unchecked_means_any_value(self, queryset, name, value):
        if value is not True:
            return None
        return queryset.filter(**{name: True})

# class IsFavoriteFilterBackend(filters.BaseFilterBackend):
#     """
#     Filter that only allows to get recipes added to favorites.
#     """

#     def filter_queryset(self, request, queryset, view):
#         return queryset.django_filters(favorite__user=request.user)


# class IsShoppingCartFilterBackend(filters.BaseFilterBackend):
#     """
#     Filter that only allows to get recipes added to shopping cart.
#     """

#     def filter_shopping_cart(self, queryset, name, value):
#         if value:
#             return queryset.filter(chopping_cart__user=self.request.user)
