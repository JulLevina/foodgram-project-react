# from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from users.models import User

from multiselectfield import MultiSelectField


class Recipe(models.Model):
    """A model for creating recipes."""

    tags = models.ManyToManyField(
        'Tag',
        through='RecipeTag',
        related_name='tags',
        verbose_name='Тэги'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='RecipeIngredient',
        related_name='ingredients',
        verbose_name='Ингредиенты'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта'
        )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Картинка'
    )
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.PositiveSmallIntegerField(verbose_name='Время приготовления')

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self) -> str:
        return self.text


class Tag(models.Model):
    """Tags for recipes."""

    name = models.CharField(  # MultiSelectField
        max_length=200,
        #choices=RECIPES_TAGS,
        verbose_name='Название тэга')
    color = models.CharField(max_length=7, default="#ffffff")
    slug = models.SlugField(
        max_length=200,
        unique=True,
    )

    def __str__(self) -> str:
        return self.name
    

class RecipeTag(models.Model):
    """Links tags to recipes."""

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tags = models.ForeignKey(Tag, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.recipe} {self.tags}'


class Ingredient(models.Model):
    """This model creates a list of ingredients."""
    
    #id = models.AutoField(primary_key=True, db_column='ingredient_id')
    name = models.CharField(
        max_length=200,
        verbose_name='Название ингредиента')
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единицы измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
    
    def __str__(self) -> str:
        return self.name


class RecipeIngredient(models.Model):
    """For counting recipe's ingredients."""

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(validators=(
            MinValueValidator(
                1, 'Минимум 1.'
            ),
        ), verbose_name='Количество ингредиентов')

    def __str__(self):
        return f'{self.ingredient} {self.amount}'

