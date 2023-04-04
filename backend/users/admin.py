from django.contrib import admin

from .models import User, Subscription


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Позволяет работать с пользовательской моделью в панели администратора.
    """

    list_display = (
        'pk',
        'email',
        'first_name',
        'last_name',
        'username'
    )
    search_fields = (
        'username',
        'email'
    )
    list_filter = (
        'email',
        'username'
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'author'
    )
    search_fields = (
        'user__email',
        'author__email'
    )
