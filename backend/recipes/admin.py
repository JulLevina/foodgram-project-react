from django.contrib import admin
from django.db.models import Count

from .models import (
    Ingredient,
    Favorite,
    Follows,
    Recipe,
    Tag,
    RecipeIngredient,
    RecipeTag,
    ShoppingCart
)


class RecipeIngredientInline(admin.StackedInline):
    """Links ingredients to recipes.
    You won't be able to create a recipe without ingredients."""

    model = RecipeIngredient
    min_num = 1


class RecipeTagInline(admin.StackedInline):
    """Links tags to recipes.
    You won't be able to create a recipe without tags."""

    model = RecipeTag
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Sets up work with the Recipe's model in the admin panel."""

    list_display = (
        'pk',
        'author',
        'name',
        'image',
        'text',
        'cooking_time',
        'pub_date',
        'favorite_count'
    )
    search_fields = (
        'name',
        'author',
        'tags'
    )
    list_filter = (
        'name',
        'author',
        'tags'
    )
    list_per_page = 6
    filter_horizontal = ['ingredients', 'tags']
    inlines = [RecipeIngredientInline, RecipeTagInline]
    empty_value_display = '-пусто-'

    def favorite_count(self, object):
        return object.favorite_count

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(favorite_count=Count('favorite'))
        return queryset


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Sets up work with the Tag's model in the admin panel."""

    list_display = (
        'pk',
        'name',
        'color',
        'slug'
    )
    search_fields = (
        'name',
    )
    list_filter = (
        'name',
    )
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Sets up work with the Ingredient's model in the admin panel."""

    list_display = (
        'name',
        'measurement_unit',
        'pk'
    )
    list_filter = (
        'name',
    )


admin.site.register(RecipeIngredient)
admin.site.register(RecipeTag)
admin.site.register(Favorite)
admin.site.register(Follows)
admin.site.register(ShoppingCart)
