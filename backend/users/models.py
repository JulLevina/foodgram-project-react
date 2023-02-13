from django.contrib.auth.models import PermissionsMixin, AbstractUser, BaseUserManager
from django.db import models


# class UserManager(BaseUserManager):
#     """
#     Django требует, чтобы кастомные пользователи определяли свой собственный
#     класс Manager. Унаследовавшись от BaseUserManager, мы получаем много того
#     же самого кода, который Django использовал для создания User (для демонстрации).
#     """

#     def create_user(self, email, password, first_name, last_name, **extra_fields):
#         """ Создает и возвращает пользователя с имэйлом, паролем и именем. """

#         user = self.model(first_name=first_name, last_name=last_name, email=email)
#         user.set_password(password)
#         user.is_staff = False
#         user.is_superuser = False
#         user.save(using=self._db)
#         user.save()
#         return user

#     def create_superuser(self, email, password, first_name, last_name, **extra_fields):
#         """ Создает и возввращет пользователя с привилегиями суперадмина. """

#         user = self.create_user(email=email, first_name=first_name, last_name=last_name, password=password)
#         user.is_active = True
#         user.is_superuser = True
#         user.is_staff = True
#         user.save()
#         return user
    
#     def get_by_natural_key(self, email_):
#         print(email_)
#         return self.get(email=email_)

class User(AbstractUser):
    """Custom User model."""

    email = models.EmailField(max_length=254, blank=False, unique=True, verbose_name='электронная почта')
    #username = models.CharField(max_length=150, blank=True, null=True, unique=True, verbose_name='имя пользователя')
    first_name = models.CharField(max_length=150, blank=False, verbose_name='имя')
    last_name = models.CharField(max_length=150, blank=False, verbose_name='фамилия')
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

    #objects = BaseUserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
    
    def get_short_name(self):
        return self.email

    def natural_key(self):
        return self.email()
    
    def __str__(self):
        return self.email
