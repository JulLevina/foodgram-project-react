from django.contrib import admin

from .models import Ingredient, Favorite, Follows, Recipe, Tag, RecipeIngredient, RecipeTag, ShoppingCart


class RecipeIngredientInline(admin.StackedInline):
    model = RecipeIngredient
    min_num = 1

class RecipeTagInline(admin.StackedInline):
    model = RecipeTag
    min_num = 1

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'author',
        'name',
        'image',
        'text',
        'cooking_time',
        'pub_date'
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


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
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
