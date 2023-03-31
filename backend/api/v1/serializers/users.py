from djoser.serializers import (
    UserCreateSerializer as DjoserUserCreateSerializer,
    UserSerializer as DjoserUserSerializer
)
from rest_framework import serializers

from users.models import User


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

    is_subscribed = serializers.BooleanField(default=False)

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
