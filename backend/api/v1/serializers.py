import base64
from django.conf import settings
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers

from recipes.models import Ingredient, Favorite, Follows, Recipe, RecipeIngredient, Tag, RecipeTag
from users.models import User


# class UserSerializer(serializers.ModelSerializer):
#     """Reterns JSON-data all of User's model fields
#     for the api/v1/users/ endpoint."""
#     is_subscribed = serializers.BooleanField()
    
#     class Meta:
#         model = User
#         fields = (
#             'id',
#             'email',
#             'username',
#             'first_name',
#             'last_name',
#             'is_subscribed'
#         )
#         model = User
    
#     # def create(self, validated_data):
#     #     user = User(
#     #         email=validated_data['email'],
#     #         username=validated_data['username']
#     #     )
#     #     user.set_password(validated_data['password'])
#     #     user.save()
#     #     return user


class UserCreateSerializer(UserCreateSerializer):
    """ """

    #is_subscribed = serializers.BooleanField()

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
            )


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

    class Meta:
        fields = (
            'id',
            'tags',
            'author',
            'is_favorited',
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
            'is_favorited',
            'name',
            'text',
            'cooking_time'
        )
        model = Recipe
    
    
    def ingredients_creating(self, ingredients, recipe, tags):
        recipe.tags.set(tags)
        RecipeIngredient.objects.filter(recipe=recipe).delete()
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(recipe=recipe,
                ingredient=ingredient.get('id'), # не получается применить get_object_or_404, но можно get('id')
                amount=ingredient.get('amount')) for ingredient in ingredients
                ] 
                )
    
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipeingredient_set')
        recipe = Recipe.objects.create(**validated_data)
        recipe.save()
        #recipe.tags.set(tags)
        self.ingredients_creating(ingredients, recipe, tags)
        return recipe
    
    def update(self, instance, validated_data):  # instance - ссфлка на объект модели Recipe,
                                                 #validated_data - словарь из проверенных данных, к-й нужно изменить
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipeingredient_set')
        super().update(instance, validated_data)
        self.ingredients_creating(ingredients, instance, tags)
        instance.save()
        return instance


# class FavoriteRecipeSerializer(serializers.ModelSerializer):
#     """Reterns JSON-data all of Favorite's model fields
#     for the api/v1/recipes/{id}/favorite endpoint"""

#     name = serializers.ReadOnlyField(source='get_name')
#     image = serializers.ReadOnlyField(source='get_image')
#     cooking_time = serializers.ReadOnlyField(source='get_cooking_time')

    
#     class Meta:
#         fields = (
#             'id',
#             'name',
#             'image',
#             'cooking_time',
#         )
#         model = Recipe
    
# class FavoriteSerializer(serializers.ModelSerializer):

#     #recipe = FavoriteRecipeSerializer(read_only=True)

#     def to_representation(self, instance):
#         ret = Favorite.to_representation(instance)
#         return ret['recipe']

#     class Meta:
#         fields = (
#             'recipe',
#         )
#         model = Favorite

class FollowSerializer(serializers.ModelSerializer):
    """Reterns JSON-data all of Follows's model fields
    for the api/v1/users/{id}/subscribe endpoint."""

    
    class Meta:
        fields = (
            'id',
        )
        model = Follows
    
    




