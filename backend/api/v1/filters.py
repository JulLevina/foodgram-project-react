from rest_framework.filters import SearchFilter
import django_filters
from django_filters.widgets import BooleanWidget

from recipes.models import Ingredient, Recipe


class IngredientFilter(SearchFilter):
    """Фильтрация списка ингредиентов по названию."""

    search_param = 'name'


class RecipeFilter(django_filters.FilterSet):
    """
    Фильтрация рецептов по автору, тэгам, избранному и списку покупок.
    """

    tags = django_filters.AllValuesMultipleFilter(
        field_name='tags__slug',
        lookup_expr='in'
    )
    is_favorited = django_filters.BooleanFilter(widget=BooleanWidget,)
    is_in_shopping_cart = django_filters.BooleanFilter(widget=BooleanWidget,)

    class Meta:
        model = Recipe
        fields = [
            'tags',
            'author',
            'is_favorited',
            'is_in_shopping_cart'
        ]
