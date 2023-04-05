from rest_framework import serializers

from recipes.models import Recipe
from users.models import Subscription, User
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
    recipes_count = serializers.IntegerField(
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

    def get_is_subscribed(self, obj):
        """Проверяет наличие у текущего пользователя подписки на автора."""
        return Subscription.objects.filter(
            user=obj.user,
            author=obj.author
        ).exists()

    def get_recipes(self, obj):
        """Возвращает все рецепты данного автора."""
        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit')
        recipes = Recipe.objects.filter(
            author=obj.author
        )
        if str(recipes_limit).isdigit():
            recipes = recipes[:int(recipes_limit)]
        return FavoriteRecipeSerializer(
            recipes,
            many=True,
            context=self.context
        ).data

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data
        author_id = self.context['request'].parser_context['kwargs']['pk']
        user = self.context['request'].user
        if Subscription.objects.filter(
            user=user,
            author_id=author_id
        ).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на данного автора.'
            )
        if not User.objects.filter(id=author_id).exists():
            raise serializers.ValidationError(
                'Автор с указанным id не существует.'
            )
        if Subscription.objects.filter(user=author_id).exists():
            raise serializers.ValidationError(
                'Подписка на самого себя невозможна.'
            )
        data['author_id'] = author_id
        data['user'] = user
        return data


class SubscribeSerializer(FollowSerializer):
    """Возвращает JSON-данные всех полей модели
    Subscription для эндпоинтв api/v1/users/subscribe/."""

    recipes_count = serializers.SerializerMethodField(
        'get_recipes_count',
        read_only=True
    )

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

    def get_recipes_count(self, obj):
        """Вычисляет общее количество рецептов автора."""
        return Recipe.objects.filter(author=obj.author).count()
