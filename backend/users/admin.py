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
    list_filter = (
        'email',
        'username'
    )


admin.site.register(Subscription)
