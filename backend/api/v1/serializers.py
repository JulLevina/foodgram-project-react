import base64
from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from recipes.models import (
    Ingredient,
    Favorite,
    Follows,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag
)
from users.models import User


class FollowsUserSerializer(serializers.ModelSerializer):
    """Reterns limited list of User's model fields."""

    email = serializers.CharField(read_only=True)
    username = serializers.CharField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)

    class Meta:
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name'
        )
        model = User


class TagSerializer(serializers.ModelSerializer):
    """Reterns JSON-data all of Tag's model fields
    for the api/v1/tags/ endpoint."""

    class Meta:
        fields = (
            'id',
            'name',
            'color',
            'slug'
        )
        model = Tag


class IngredientReadSerializer(serializers.ModelSerializer):
    """Reterns JSON-data all of Ingredient's model fields
    for the api/v1/engredients/ endpoint."""

    class Meta:
        fields = (
            'id',
            'name',
            'measurement_unit'
        )
        model = Ingredient


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Adds an amount of ingredients into recipe."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        fields = (
            'id',
            'amount',
        )
        model = Ingredient


class IngredientWriteSerializer(serializers.ModelSerializer):
    """Reterns JSON-data all of Ingredient's model fields
    for the api/v1/engredients/ endpoint."""

    id = serializers.IntegerField(read_only=True, source='ingredient.id')
    name = serializers.CharField(read_only=True, source='ingredient.name')
    measurement_unit = serializers.CharField(
        read_only=True,
        source='ingredient.measurement_unit'
    )

    class Meta:
        fields = (
            'id',
            'name',
            'amount',
            'measurement_unit'
        )
        model = RecipeIngredient


class Base64ImageField(serializers.ImageField):
    """Encodes the images to base64."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class RecipeReadSerializer(serializers.ModelSerializer):
    """Read-only data.
    Reterns JSON-data all of Recipe's model fields
    for the api/v1/recipes/ endpoint.
    """

    tags = TagSerializer(read_only=True, many=True)
    ingredients = IngredientWriteSerializer(many=True, source='recipe')
    author = FollowsUserSerializer(
        read_only=True)
    is_favorited = serializers.SerializerMethodField(source='get_is_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField(
        'get_is_in_shopping_cart'
    )

    def get_is_favorited(self, object) -> bool:
        """Indicates a status of the recipe: is it favorite or not."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user__username=user, recipe=object).exists()

    def get_is_in_shopping_cart(self, object) -> bool:
        """Indicates a status of the recipe: is it in shopping cart or not."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user__username=user,
            recipe=object
        ).exists()

    class Meta:
        fields = (
            'id',
            'tags',
            'author',
            'is_favorited',
            'is_in_shopping_cart',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )
        model = Recipe


class RecipeWriteSerializer(serializers.ModelSerializer):
    """For data recording only.
    Reterns JSON-data all of Recipe's model fields
    for the api/v1/recipes/ endpoint.
    """

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField(required=False, allow_null=False)
    ingredients = RecipeIngredientSerializer(many=True, allow_null=False)
    author = FollowsUserSerializer(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance, context={'request': self.context.get('request')}
        ).data

    class Meta:
        fields = (
            'ingredients',
            'tags',
            'image',
            'author',
            'name',
            'text',
            'cooking_time'
        )
        model = Recipe

    def validate_cooking_time(self, value):
        """Ckecking for positive cooking time."""
        if not (value > 0):
            raise serializers.ValidationError(
                'Время приготовления не может быть меньше либо равно 0 минут!'
                )
        return value

    def validate_ingredients(self, ingredients):
        """Checking for creating recipe without ingredients."""
        if not ingredients:
            raise serializers.ValidationError(
                'Создание рецепта без ингредиентов невозможно!'
                )
        for ingredient in ingredients:
            if not (int(ingredient.get('amount')) > 1):
                raise serializers.ValidationError(
                    'Количнество ингредиентов должно быть больше 0!'
                    )
            sorted_ingredients = []
            for key in ingredient:
                sorted_ingredients.append(key)
                if len(sorted_ingredients) != len(set(sorted_ingredients)):
                    raise serializers.ValidationError(
                        'Ингредиенты не должны повторяться!'
                        )
        return ingredients

    def ingredients_creating(self, ingredients, recipe, tags):
        """Creates all the objects ingredients data for recipe. """
        recipe.tags.set(tags)
        RecipeIngredient.objects.filter(recipe=recipe).delete()
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    recipe=recipe,
                    ingredient_id=ingredient.get('id'),
                    amount=ingredient.get('amount')
                ) for ingredient in ingredients
            ]
        )

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.save()
        recipe.tags.set(tags)
        self.ingredients_creating(ingredients, recipe, tags)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        super().update(instance, validated_data)
        self.ingredients_creating(ingredients, instance, tags)
        instance.save()
        return instance


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    """Reterns JSON-data all of Favorite's model fields
    for the api/v1/recipes/{id}/favorite endpoint"""

    name = serializers.CharField(read_only=True)
    image = serializers.SerializerMethodField('get_image_url', read_only=True)
    cooking_time = serializers.IntegerField(read_only=True)

    def get_image_url(self, object):
        """Returns the url of the image."""
        return object.image.url

    class Meta:
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
        model = Recipe


class FavoriteSerializer(serializers.ModelSerializer):
    """Reterns JSON-data all of Favorite's model fields
    for the api/v1/users/favorite/ endpoint."""

    recipe = FavoriteRecipeSerializer(read_only=True)

    def to_representation(self, instance):
        """Convert recipe's to list of fields."""
        ret = super().to_representation(instance)
        return ret['recipe']

    class Meta:
        fields = (
            'recipe',
        )
        model = Favorite


class FollowSerializer(serializers.ModelSerializer):
    """Reterns JSON-data all of Follow's model fields
    for the api/v1/users/subscribe/ and
    api/v1/users/subscribtions/ endpoints."""

    email = serializers.CharField(
        read_only=True,
        source='author.email'
    )
    id = serializers.IntegerField(
        read_only=True,
        source='author.id'
    )
    username = serializers.CharField(
        read_only=True,
        source='author.username'
    )
    first_name = serializers.CharField(
        read_only=True,
        source='author.first_name'
    )
    last_name = serializers.CharField(
        read_only=True,
        source='author.last_name'
    )
    is_subscribed = serializers.SerializerMethodField(
        'get_is_subscribed',
        read_only=True
    )
    recipes_count = serializers.SerializerMethodField(
        'get_recipes_count',
        read_only=True
    )
    recipes = serializers.SerializerMethodField('get_recipes', read_only=True)

    def get_is_subscribed(self, object):
        """Checks the subscription to the author."""
        return Follows.objects.filter(
            user=object.user,
            author=object.author
        ).exists()

    def get_recipes_count(self, object):
        """Counts the total number of recipes of this author."""
        return Recipe.objects.filter(author=object.author).count()

    def get_recipes(self, object):
        """Shows all the author's recipes."""
        recipes = Recipe.objects.filter(author=object.author)
        return FavoriteRecipeSerializer(recipes, many=True).data

    class Meta:
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        model = Follows


class UserCreateSerializer(UserCreateSerializer):
    """Reterns JSON-data all of User's model fields
    for the api/v1/users/ endpoint."""

    class Meta(UserCreateSerializer.Meta):
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )
        model = User


class CustomUserSerialiser(UserSerializer):
    """Sterilizer for checking user's subscriptions to authors."""

    is_subscribed = serializers.SerializerMethodField(
        'get_is_subscribed',
        read_only=True
    )

    def get_is_subscribed(self, object):
        """Checks the subscription to the author."""
        user = self.context.get('request').user
        return Follows.objects.filter(user=user, author=object).exists()

    class Meta(UserSerializer.Meta):
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )
        model = User


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Reterns JSON-data all of ShoppingCart's model fields
    for the api/v1/recipes/{id}/shopping_cart endpoint."""

    recipe = FavoriteRecipeSerializer(read_only=True)

    def to_representation(self, instance):
        """Convert recipe's to list of fields."""
        ret = super().to_representation(instance)
        return ret['recipe']

    class Meta:
        fields = (
            'recipe',
        )
        model = ShoppingCart
