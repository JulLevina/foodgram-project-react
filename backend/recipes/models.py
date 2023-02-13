from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from users.models import User

#from multiselectfield import MultiSelectField

class Recipe(models.Model):
    """A model for creating recipes."""

    tags = models.ManyToManyField(
        'Tag',
        through='RecipeTag',
        related_name='tags',
        verbose_name='Тэги'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
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
    is_favorited = models.ManyToManyField(User, related_name='favorites',  blank=True, verbose_name='Избранное')
    is_shopping_cart = models.BooleanField(verbose_name='Список покупок', default=False)
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата публикации')

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
    
    @property
    def get_name(self):
        if self.parent is not None:
            return Recipe.objects.get(id=self.parent.id).name
        return self.name
    
    @property
    def get_image(self):
        if self.parent is not None:
            return Recipe.objects.get(id=self.parent.id).image
        return self.image
    
    @property
    def get_cookihg_time(self):
        if self.parent is not None:
            return Recipe.objects.get(id=self.parent.id).cooking_time
        return self.cooking_time

    def __str__(self) -> str:
        return self.text


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
    

class RecipeTag(models.Model):
    """Links tags to recipes."""

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tags = models.ForeignKey(Tag, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.recipe} {self.tags}'


class Ingredient(models.Model):
    """This model creates a list of ingredients."""
    
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
        return f'{self.name} {self.measurement_unit}'


class RecipeIngredient(models.Model):
    """For counting recipe's ingredients."""

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(validators=(
            MinValueValidator(
                1, 'Минимум 1.'
            ),
        ), verbose_name='Количество ингредиентов')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]
    
    def __str__(self):
        return f'{self.ingredient} {self.amount}'


class Favorite(models.Model):
    """Adds recipes to favorites."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        #related_name='follower',
        verbose_name='Подписчик'
    )
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_recipe'
            )
        ]

    def __str__(self):
        return f'{self.user} {self.recipe}'



class ChoppingCart(models.Model):
    """Adds recipes to shopping_cart."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        #related_name='follower',
        verbose_name='Подписчик'
    )
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_recipe'
            )
        ]

    def __str__(self):
        return f'{self.user} {self.recipe}'


class Follows(models.Model):
    """For user subscriptions."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_follow'
            )
        ]

    def __str__(self):
        return f'{self.user} {self.author}'
