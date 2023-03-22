import base64
from django.db import transaction
from django.core.files.base import ContentFile
from rest_framework import serializers

from recipes.models import (
    Favorite,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag
)
from .tags import TagSerializer
from .ingredients import IngredientWriteSerializer, RecipeIngredientSerializer
from .users import UserSerializer


class Base64ImageField(serializers.ImageField):
    """Кодирует изображения в base64."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)

    #def to_representation(self, value):
        #return value.url


class RecipeReadSerializer(serializers.ModelSerializer):
    """Только для чтения.
    Возвращает JSON-данные всех полей модели
    Recipe для эндпоинта api/v1/recipes/.
    """

    image = Base64ImageField()
    tags = TagSerializer(read_only=True, many=True)
    ingredients = IngredientWriteSerializer(many=True, source='recipes')
    author = UserSerializer(read_only=True)
    is_favorited = serializers.BooleanField(default=False)
    is_in_shopping_cart = serializers.BooleanField(default=False)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    # def get_is_favorited(self, obj) -> bool:
    #     """Определяет, добавлен ли рецепт в избранное."""
    #     user = self.context.get('request').user
    #     if user.is_anonymous:
    #         return False
    #     return Favorite.objects.filter(
    #         user=user, recipe=obj).exists()

    # def get_is_in_shopping_cart(self, obj) -> bool:
    #     """Определяет, добавлен ли рецепт в список покупок."""
    #     user = self.context.get('request').user
    #     if user.is_anonymous:
    #         return False
    #     return ShoppingCart.objects.filter(
    #         user=user,
    #         recipe=obj
    #     ).exists()


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Только для записи.
    Возвращает JSON-данные всех полей модели
    Recipe для эндпоинта api/v1/recipes/.
    """

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField(required=False, allow_null=True) #use_url=True, required=True, allow_null=False)
    ingredients = RecipeIngredientSerializer(many=True, allow_null=False)

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'ingredients',
            'image',
            'name',
            'text',
            'cooking_time'
        )
        read_only_fields = ['author']

    def validate_ingredients(self, ingredients):
        """Предотвращает создание рецепта без ингредиентов.
        Предотвращает дублирование ингредиентов в рецепте."""
        if not ingredients:
            raise serializers.ValidationError(
                'Создание рецепта без ингредиентов невозможно!'
                )
        for ingredient in ingredients:
            if not (int(ingredient.get('amount')) >= 1):
                raise serializers.ValidationError(
                    'Количнество ингредиентов должно быть больше 0!'
                    )
            sorted_ingredients = []
            for key in ingredient:
                sorted_ingredients.append(key)
                if len(sorted_ingredients) != len(set(sorted_ingredients)):
                    raise serializers.ValidationError(
                        'Ингредиенты не должны повторяться!'
                        )
        return ingredients

    @transaction.atomic
    def ingredients_creating(self, ingredients, recipe, tags):
        """Создает набор полей для добавления ингредиентов в рецепт. """
        recipe.tags.set(tags)
        RecipeIngredient.objects.filter(recipe=recipe).delete()
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    recipe=recipe,
                    ingredient_id=ingredient.get('id'),
                    amount=ingredient.get('amount')
                ) for ingredient in ingredients
            ]
        )

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = super().create(validated_data)
        recipe.tags.set(tags)
        self.ingredients_creating(ingredients, recipe, tags)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        super().update(instance, validated_data)
        self.ingredients_creating(ingredients, instance, tags)
        instance.save()
        return instance

    def to_representation(self, instance):
        """Отображает созданный рецепт в форме для чтения."""
        return RecipeReadSerializer(
            instance, context={'request': self.context.get('request')}
        ).data
