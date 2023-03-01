from rest_framework import serializers

from recipes.models import Favorite, Recipe


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    """
    Возвращает JSON-данные, необходимые для добавления рецепта в избранное.
    """

    name = serializers.CharField(read_only=True)
    image = serializers.SerializerMethodField('get_image_url', read_only=True)
    cooking_time = serializers.IntegerField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )

    def get_image_url(self, object):
        """Возвращает url изображения рецепта."""
        return object.image.url


class FavoriteSerializer(serializers.ModelSerializer):
    """Возвращает JSON-данные всех полей модели
    Favorite для эндпоинта api/v1/users/favorite/."""

    recipe = FavoriteRecipeSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = (
            'recipe',
        )

    def to_representation(self, instance):
        """Преобразует информацию о рецепте в список полей."""
        ret = super().to_representation(instance)
        return ret['recipe']