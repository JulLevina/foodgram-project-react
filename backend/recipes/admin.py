from django.contrib import admin

from .models import Ingredient, Recipe, Tag, RecipeIngredient, RecipeTag


class RecipeIngredientInline(admin.StackedInline):
    model = RecipeIngredient
    min_num = 1

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'author',
        'name',
        'image',
        'text',
        'cooking_time'
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
    inlines = [RecipeIngredientInline]
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


admin.site.register(Ingredient)
admin.site.register(RecipeIngredient)
admin.site.register(RecipeTag)
