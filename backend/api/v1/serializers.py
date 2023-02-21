import collections
import base64
from django.conf import settings
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (
    Ingredient,
    Favorite,
    Follows,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag
)
from users.models import User


class FollowsUserSerializer(serializers.ModelSerializer):

    email = serializers.CharField(read_only=True)
    username = serializers.CharField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    # is_subscribed = serializers.SerializerMethodField('get_id_subscribed',)
    # #recipe = serializers.SerializerMethodField('get_following_recipes', read_only=True)

    # def get_id_subscribed(self, object):
    #     user = self.context.get('request').user
    #     return Follows.objects.filter(user__username=user, author=object).exists()

    class Meta:
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            #'is_subscribed'
            #'recipe'
        )
        model = User


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


class IngredientReadSerializer(serializers.ModelSerializer):
    """Reterns JSON-data all of Ingredient's model fields
    for the api/v1/engredients/ endpoint."""

    class Meta:
        fields = (
            'id',
            'name',
            'measurement_unit'
        )
        model = Ingredient


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Adds an amount of ingredients into recipe."""

    id = serializers.IntegerField()#PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()
    
    
    class Meta:
        fields = (
            'id',
            'amount',
        )
        model = Ingredient # RecipeIngredient


class IngredientWriteSerializer(serializers.ModelSerializer):
    """Reterns JSON-data all of Ingredient's model fields
    for the api/v1/engredients/ endpoint."""

    # amount = serializers.SerializerMethodField('get_ingredient_amount')

    # def get_ingredient_amount(self, obj):
    #     """Returns an ingredients amount for the recipe."""
    #     amount = RecipeIngredient.objects.get(ingredient=obj).amount
    #     return amount
    
    id = serializers.IntegerField(read_only=True, source='ingredient.id')
    name = serializers.CharField(read_only=True, source='ingredient.name')
    measurement_unit = serializers.CharField(read_only=True, source='ingredient.measurement_unit')

    class Meta:
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )
        model = RecipeIngredient


# l = IngredientWriteSerializer(instance=RecipeIngredient.objects.first())
# print(l.data)

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
    ingredients = IngredientWriteSerializer(many=True, source='recipe')
    author = FollowsUserSerializer(
        read_only=True)
    is_favorited = serializers.SerializerMethodField(source='get_is_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField('get_is_in_shopping_cart')

    def get_is_favorited(self, object):
        """Returns ..."""
        user = self.context.get('request').user
        return Favorite.objects.filter(user__username=user, recipe=object).exists()
    
    def get_is_in_shopping_cart(self, object):
        """Returns ..."""
        user = self.context.get('request').user
        return ShoppingCart.objects.filter(user__username=user, recipe=object).exists() 
        

    class Meta:
        fields = (
            'id',
            'tags',
            'author',
            'is_favorited',
            'is_in_shopping_cart',
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
    ingredients = RecipeIngredientSerializer(many=True, allow_null=False)
    author = FollowsUserSerializer(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    
    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context={'request': self.context.get('request')}).data
    
    class Meta:
        fields = (
            'ingredients',
            'tags',
            'image',
            'author',
            #'is_favorited',
            'name',
            'text',
            'cooking_time'
        )
        model = Recipe
    
    def validate_cooking_time(self, value):
        """Ckecking for positive cooking time."""
        if not (value > 0):
            raise serializers.ValidationError(
                'Время приготовления не может быть меньше либо равно 0 минут!'
                )
        return value
    
    def validate_ingredients(self, ingredients):
        """Checking for creating recipe without ingredients."""
        if not ingredients:
            raise serializers.ValidationError(
                'Создание рецепта без ингредиентов невозможно!'
                )
        for ingredient in ingredients:
            if not (int(ingredient.get('amount')) > 1):
                raise serializers.ValidationError(
                    'Количнество ингредиентов должно быть больше 0!'
                    )
            sorted_ingredients = []
            for key in ingredient:
                sorted_ingredients.append(key)
                if len(sorted_ingredients) != len(set(sorted_ingredients)):
                    raise serializers.ValidationError(
                        'Создание рецепта с одинаковыми ингредиентами невозможно!'
                        )
        return ingredients

    def ingredients_creating(self, ingredients, recipe, tags):
        """Creates all the objects ingredients data for recipe. """
        recipe.tags.set(tags)
        RecipeIngredient.objects.filter(recipe=recipe).delete()
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(recipe=recipe,
                ingredient_id=ingredient.get('id'), # не получается применить get_object_or_404, но можно get('id')
                amount=ingredient.get('amount')) for ingredient in ingredients
                ] 
                )
    
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.save()
        #recipe.tags.set(tags)
        self.ingredients_creating(ingredients, recipe, tags)
        return recipe
    
    def update(self, instance, validated_data):  # instance - ссфлка на объект модели Recipe,
                                                 #validated_data - словарь из проверенных данных, к-й нужно изменить
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        super().update(instance, validated_data)
        self.ingredients_creating(ingredients, instance, tags)
        instance.save()
        return instance


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    """Reterns JSON-data all of Favorite's model fields
    for the api/v1/recipes/{id}/favorite endpoint"""

    name = serializers.CharField(read_only=True)
    #image = serializers.CharField(source='image.url', read_only=True)
    cooking_time = serializers.IntegerField(read_only=True)
    # name = serializers.ReadOnlyField(source="get_name")
    # image = serializers.ReadOnlyField(source="get_image")
    # cooking_time = serializers.ReadOnlyField(source="get_cooking_time")
    
    class Meta:
        fields = (
            'id',
            'name',
            #'image',
            'cooking_time',
        )
        model = Recipe
    
class FavoriteSerializer(serializers.ModelSerializer):

    recipe = FavoriteRecipeSerializer(read_only=True)

    def to_representation(self, instance):
        """Convert recipe's to list of fields."""
        ret = super().to_representation(instance)
        return ret['recipe']

    class Meta:
        fields = (
            'recipe',
        )
        model = Favorite


class FollowSerializer(serializers.ModelSerializer):

    author = FollowsUserSerializer(read_only=True)
    #user = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())
    # is_subscribed = serializers.BooleanField(read_only=True)
    # recipes = FavoriteRecipeSerializer(read_only=True, many=True)

    def to_representation(self, instance):
        """Convert follow's to list of fields."""
        ret = super().to_representation(instance)
        return ret['author']
    
    class Meta:
        fields = (
            'author',
            'user'
           
            # 'is_subscribed',
            # 'recipes'
        )
        model = Follows


# class IsSubscribedSerializer(serializers.ModelSerializer):
#     model 

class UserCreateSerializer(UserCreateSerializer):
    """Reterns JSON-data all of User's model fields
    for the api/v1/users/ endpoint."""
    is_subscribed = serializers.SerializerMethodField('get_id_subscribed', read_only=True)

    def get_id_subscribed(self, object):
        user = self.context.get('request').user
        return Follows.objects.filter(user=user, author=object).exists()

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
            'is_subscribed'
            )


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Reterns JSON-data all of ShoppingCart's model fields
    for the api/v1/recipes/{id}/shopping_cart endpoint."""
    
    recipe = FavoriteRecipeSerializer(read_only=True)

    def to_representation(self, instance):
        """Convert recipe's to list of fields."""
        ret = super().to_representation(instance)
        return ret['recipe']
    
    class Meta:
        fields = (
            'recipe',
        )
        model = ShoppingCart


class DownloadShoppinCartSerializer(serializers.ModelSerializer):
    pass
    # recipe = IngredientWriteSerializer(read_only=True, many=True)

    # def to_representation(self, instance):
    #     """Convert ingredients to list of fields."""
    #     ret = super().to_representation(instance)
    #     return ret['recipe.ingredients']
    
    # class Meta:
    #     fields = (
    #         'recipe',
    #     )
    #     model = ShoppingCart
# l = DownloadShoppinCartSerializer(instance=Ingredient.objects.first())
# print(l.data)
    




