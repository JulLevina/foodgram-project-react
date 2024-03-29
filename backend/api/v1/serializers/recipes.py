import base64
from django.db import transaction
from django.core.files.base import ContentFile
from rest_framework import serializers

from recipes.models import (
    Recipe,
    Ingredient,
    RecipeIngredient,
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


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Только для записи.
    Возвращает JSON-данные всех полей модели
    Recipe для эндпоинта api/v1/recipes/.
    """

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField(
        max_length=None,
        use_url=True,
        required=True
    )
    ingredients = RecipeIngredientSerializer(many=True)

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

    def validate_ingredients(self, value):
        """Предотвращает создание рецепта без ингредиентов.
        Предотвращает дублирование ингредиентов в рецепте."""
        if not value:
            raise serializers.ValidationError(
                'Создание рецепта без ингредиентов невозможно!'
            )
        for ingredient in value:
            if not (int(ingredient.get('amount')) >= 1):
                raise serializers.ValidationError(
                    'Количество ингредиентов должно быть больше 0!'
                )
            if not Ingredient.objects.filter(id=ingredient['id']).exists():
                raise serializers.ValidationError(
                    'Ингредиент с указанным id не существует!'
                )
        return value

    def validate(self, data):
        ingredients = data['ingredients']
        sorted_ingredients = []
        for ingredient in ingredients:
            if ingredient in sorted_ingredients:
                raise serializers.ValidationError(
                    'Ингредиенты не должны повторяться!'
                )
            sorted_ingredients.append(ingredient)
        return data

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
        return instance

    def to_representation(self, instance):
        """Отображает созданный рецепт в форме для чтения."""
        return RecipeReadSerializer(
            instance, context={'request': self.context.get('request')}
        ).data
