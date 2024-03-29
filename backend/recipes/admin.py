from django.contrib import admin
from django.db.models import Count

from .models import (
    Ingredient,
    Favorite,
    Recipe,
    Tag,
    RecipeIngredient,
    RecipeTag,
    ShoppingCart
)


class RecipeIngredientInline(admin.TabularInline):
    """Связывает ингредиенты с рецептами.
    Предотвращает возможность создания рецепта без ингредиентов."""

    model = RecipeIngredient
    extra = 1


class RecipeTagInline(admin.TabularInline):
    """Связывает тэги с рецептами.
    Предотвращает возможность создания рецепта без тэгов."""

    model = RecipeTag
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Позволяет работать с моделью рецептов в панели администратора."""

    list_display = (
        'pk',
        'author',
        'name',
        'image',
        'text',
        'cooking_time',
        'pub_date',
        'favorites_count'
    )
    search_fields = (
        'name',
        'author__email',
        'tags__name',
    )
    list_filter = (
        'name',
        'author',
        'tags'
    )
    list_per_page = 6
    filter_horizontal = ('ingredients', 'tags')
    inlines = (RecipeIngredientInline, RecipeTagInline)
    empty_value_display = '-пусто-'

    def favorites_count(self, object):
        return object.favorites_count

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(favorites_count=Count('favorites'))


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Позволяет работать с моделью тэгов в панели администратора."""

    list_display = (
        'pk',
        'name',
        'color',
        'slug'
    )
    prepopulated_fields = {'slug': ('name',)}
    search_fields = (
        'name',
    )
    list_filter = (
        'name',
    )
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Позволяет работать с моделью ингредиентов в панели администратора."""

    list_display = (
        'name',
        'measurement_unit',
        'pk'
    )
    search_fields = (
        'name',
    )
    list_filter = (
        'name',
    )


admin.site.register(RecipeIngredient)
admin.site.register(RecipeTag)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)
