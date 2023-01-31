# from django.conf import settings
from django.db import models
from users.models import User

class Recipe(models.Model):
    """A model for creating recipes."""

    tags = models.ManyToManyField(
        'Tags',
        through='Tag',
        related_name='tags',
        verbose_name='Тэги'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    ingredients = models.ManyToManyField(
        'Ingredients',
        through='Ingredient',
        related_name='ingredients',
        verbose_name='Тэги'
    )
    # is_favorited = models.BooleanField(
    #     verbose_name='Находится ли в избранном'
    # )
    # is_in_shopping_cart = models.BooleanField(
    #     verbose_name='Находится ли в корзине'
    # )
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта'
        )
    image = models.ImageField(
        upload_to='foodgram/',
        verbose_name='Картинка'
    )
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.PositiveSmallIntegerField(verbose_name='Время приготовления')

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self) -> str:
        return self.text


# class Subscribtions(models.Model):
#     """А model for subscriptions to recipes."""


class Tag(models.Model):
    """Tags for recipes."""
    name = models.CharField(
        max_length=200,
        verbose_name='Название тэга')
    color = models.CharField(max_length=7, default="#ffffff")
    slug = models.SlugField(
        max_length=200,
        unique=True,
    )

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    """This model creates a list of ingredients."""
    name = models.CharField(
        max_length=200,
        verbose_name='Название ингредиента')
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единицы измерения'
    )

    def __str__(self) -> str:
        return self.name

# class FavoriteRecipes(models.Model):
#     """This model adds recipes to favorites."""


# class ShoppingCart(models.Model):
#     """This model creates a shopping list"""
