from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Предоставляет право изменения контента только автору.
    """

    message = (
        'Для создания контента необходимо обладать '
        'правами автора.'
    )

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )
