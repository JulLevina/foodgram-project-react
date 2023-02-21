import django_filters

from recipes.models import Recipe


class RecipeFilter(django_filters.FilterSet):
    """Фильтрация произведений по жанру, категории, названию, году."""

    tags = django_filters.CharFilter(field_name='tags__slug')

    class Meta:
        model = Recipe
        fields = (
            'tags',
        )