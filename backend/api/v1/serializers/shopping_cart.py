from rest_framework import serializers

from recipes.models import ShoppingCart
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

    def to_representation(self, instance):
        """Преобразует информацию о рецепте в список полей."""
        ret = super().to_representation(instance)
        return ret['recipe']