import base64
from django.conf import settings
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag, RecipeTag
from users.models import User


class TagSerializer(serializers.ModelSerializer):
    """Reterns JSON-data all of Tag's model fields
    for the api/v1/tags/ endpoint."""

    class Meta:
        fields = (
            'id',
            'name',
            'color',
            'slug'
        )
        model = Tag


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Adds an amount of ingredients into recipe."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=1)
    
    
    class Meta:
        fields = (
            'id',
            'amount',
        )
        model = RecipeIngredient


class IngredientSerializer(serializers.ModelSerializer):
    """Reterns JSON-data all of Ingredient's model fields
    for the api/v1/engredients/ endpoint."""
    amount = serializers.SerializerMethodField('get_ingredient_amount')

    def get_ingredient_amount(self, obj):
        amount = RecipeIngredient.objects.get(ingredient=obj).amount
        return amount
    
    class Meta:
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )
        model = Ingredient


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')  
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class RecipeReadSerializer(serializers.ModelSerializer):
    """Read-only data.
    Reterns JSON-data all of Recipe's model fields
    for the api/v1/recipes/ endpoint.
    """

    tags = TagSerializer(read_only=True, many=True)
    ingredients = IngredientSerializer(read_only=True, many=True)
    print(ingredients)

    class Meta:
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )
        model = Recipe

class RecipeWriteSerializer(serializers.ModelSerializer):
    """For data recording only.
    Reterns JSON-data all of Recipe's model fields
    for the api/v1/recipes/ endpoint.
    """

    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    image = Base64ImageField(required=False, allow_null=True) # change on True
    ingredients = RecipeIngredientSerializer(source='recipeingredient_set', many=True)
    
    
    class Meta:
        fields = (
            'ingredients',
            'tags',
            'image',
            'author',
            'name',
            'text',
            'cooking_time'
        )
        model = Recipe
    
    
    def ingredients_creating(self, ingredients, recipe):
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(recipe=recipe,
                ingredient=ingredient.get('id'),
                amount=ingredient.get('amount')) for ingredient in ingredients
                ] 
                )
    
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipeingredient_set')
        recipe = Recipe.objects.create(**validated_data)
        recipe.save()
        recipe.tags.set(tags)
        self.ingredients_creating(ingredients, recipe)
        return recipe
    
    # def update(self, instance, validated_data):

    #     return super().update(instance, validated_data)

