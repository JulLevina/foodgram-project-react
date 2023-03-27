from djoser.serializers import (
    UserCreateSerializer as DjoserUserCreateSerializer,
    UserSerializer as DjoserUserSerializer
)
from rest_framework import serializers

from users.models import User, Subscription


class UserCreateSerializer(DjoserUserCreateSerializer):
    """Возвращает JSON-данные всех полей модели
    User для эндпоинтов api/v1/users/."""

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )


class UserSerializer(DjoserUserSerializer):
    """Возвращает данные о подписчиках."""

    is_subscribed = serializers.SerializerMethodField(
        'get_is_subscribed',
        read_only=True
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        """Проверяет наличие у текущего пользователя подписки на автора.."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(user=user, author=obj).exists()
