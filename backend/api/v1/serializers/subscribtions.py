from rest_framework import serializers

from recipes.models import Recipe
from users.models import Subscription
from .favorites import FavoriteRecipeSerializer


class FollowSerializer(serializers.ModelSerializer):
    """Возвращает JSON-данные всех полей модели
    Subscription для эндпоинтов api/v1/users/subscribe/
    и api/v1/users/subscribtions/."""

    email = serializers.CharField(
        read_only=True,
        source='author.email'
    )
    id = serializers.IntegerField(
        read_only=True,
        source='author.id'
    )
    username = serializers.CharField(
        read_only=True,
        source='author.username'
    )
    first_name = serializers.CharField(
        read_only=True,
        source='author.first_name'
    )
    last_name = serializers.CharField(
        read_only=True,
        source='author.last_name'
    )
    is_subscribed = serializers.SerializerMethodField(
        'get_is_subscribed',
        read_only=True
    )
    recipes_count = serializers.SerializerMethodField(
        'get_recipes_count',
        read_only=True
    )
    recipes = serializers.SerializerMethodField('get_recipes', read_only=True)

    class Meta:
        model = Subscription
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_is_subscribed(self, object):
        """Проверяет наличие у текущего пользователя подписки на автора."""
        return Subscription.objects.filter(
            user=object.user,
            author=object.author
        ).exists()

    def get_recipes_count(self, object):
        """Вычисляет общее количество рецептов автора."""
        return Recipe.objects.filter(author=object.author).count()

    def get_recipes(self, object):
        """Возвращает все рецепты данного автора."""
        recipes = Recipe.objects.filter(author=object.author)
        return FavoriteRecipeSerializer(recipes, many=True).data
