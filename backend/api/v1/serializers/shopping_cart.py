from rest_framework import serializers

from recipes.models import ShoppingCart, Recipe
from .favorites import FavoriteRecipeSerializer


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Возвращает JSON-данные всех полей модели
    ShoppingCart для эндпоинта api/v1/recipes/{id}/shopping_cart."""

    recipe = FavoriteRecipeSerializer(read_only=True)

    class Meta:
        model = ShoppingCart
        fields = (
            'recipe',
        )

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data
        recipe_id = self.context['request'].parser_context['kwargs']['pk']
        user = self.context['request'].user
        if ShoppingCart.objects.filter(
            user=user,
            recipe_id=recipe_id
        ).exists():
            raise serializers.ValidationError(
                'Вы уже добавили данный рецепт в список покупок.'
            )
        if not Recipe.objects.filter(id=recipe_id).exists():
            raise serializers.ValidationError(
                'Рецепт с указанным id не существует.'
            )
        data['recipe_id'] = recipe_id
        data['user'] = user
        return data

    def create(self, validated_data):
        return ShoppingCart.objects.create(**validated_data)

    def to_representation(self, instance):
        """Преобразует информацию о рецепте в список полей."""
        ret = super().to_representation(instance)
        return ret['recipe']
