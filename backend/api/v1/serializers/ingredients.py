from rest_framework import serializers

from recipes.models import Ingredient, RecipeIngredient


class IngredientReadSerializer(serializers.ModelSerializer):
    """Только для чтения.
    Возвращает JSON-данные всех полей модели
    Ingredient для эндпоинта api/v1/engredients/."""

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Добавляет количество ингредиентов в рецепт."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'amount',
        )


class IngredientWriteSerializer(serializers.ModelSerializer):
    """Только для записи.
    Возвращает название, единицы измерения и количество ингредиентов."""

    id = serializers.IntegerField(read_only=True, source='ingredient.id')
    name = serializers.CharField(read_only=True, source='ingredient.name')
    measurement_unit = serializers.CharField(
        read_only=True,
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )
