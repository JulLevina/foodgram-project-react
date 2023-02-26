from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Sets up work with the User's model in the admin panel."""

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
