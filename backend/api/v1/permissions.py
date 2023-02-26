from rest_framework import permissions


class IsAuthorOrAdminOrReadOnly(permissions.BasePermission):
    """
    Grants the right to create content to the administrator and the author.
    """

    message = (
        'Для создания контента необходимо обладать '
        'правами администратора или автора.'
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
            or request.user.is_admin
        )


class AdminOrReadOnly(permissions.BasePermission):
    """Grants the right to create content to the administrator."""

    message = 'Только для администратора!'

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_admin
        )
