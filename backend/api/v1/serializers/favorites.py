from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import Favorite, Recipe


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    """
    Возвращает JSON-данные, необходимые для добавления рецепта в избранное.
    """
    #image = serializers.SerializerMethodField('get_image')  # новое

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ['name', 'image', 'cooking_time']

    #def get_image(self, obj):  # новое
        #self.context['request'].build_absolute_uri(obj.image.url)


class FavoriteSerializer(serializers.ModelSerializer):
    """Возвращает JSON-данные всех полей модели
    Favorite для эндпоинта api/v1/users/favorite/."""

    recipe = FavoriteRecipeSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = (
            'recipe',
            'user'
        )
        # validators = (  # не работает валидация так
        #     UniqueTogetherValidator(
        #         queryset=Favorite.objects.all(),
        #         fields=('user', 'recipe'),
        #         message='Вы уже добавили данный рецепт в избранное.',
        #     ),
        # )

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data
        recipe_id = self.context['request'].parser_context['kwargs']['pk']
        user = self.context['request'].user
        if Favorite.objects.filter(user=user, recipe_id=recipe_id).exists():
            raise serializers.ValidationError(
                'Вы уже добавили данный рецепт в избранное.'
            )
        if not Recipe.objects.filter(id=recipe_id).exists():
            raise serializers.ValidationError(
                'Рецепт с указанным id не существует.'
            )
        data['recipe_id'] = recipe_id
        data['user'] = user
        return data

    def to_representation(self, instance):
        """Преобразует информацию о рецепте в список полей."""
        ret = super().to_representation(instance)
        return ret['recipe']
