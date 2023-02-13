from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User

# @admin.register(User, UserAdmin)
# class RecipeAdmin(admin.ModelAdmin):
#     list_display = (
#         'pk',
#         'username',
#         'email',
#         'first_name',
#         'last_name',
#     )

admin.site.register(User, UserAdmin)