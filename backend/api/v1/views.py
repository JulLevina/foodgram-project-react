from rest_framework import mixins, viewsets

from recipes.models import Ingredient, Recipe, Tag
from users.models import User
from api.v1.serializers import IngredientSerializer, RecipeIngredientSerializer, RecipeReadSerializer, RecipeWriteSerializer, TagSerializer

class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Performs all operations with ingredients.
    Handles all requests for the api/v1/ingreients/ endpoint."""

    queryset = Ingredient.objects.all() # order_by('name')
    serializer_class = IngredientSerializer

    # def get_serializer_class(self):
    #     if self.action in {'create', 'partial_update'}:
    #         return RecipeIngredientAmountSerializer
    #     return IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """Performs all operations with recipes.
    Handles all requests for the api/v1/recipes/ endpoint."""

    queryset = Recipe.objects.all()
    # serializer_class = RecipeWriteSerializer
    http_method_names = ('get', 'post', 'patch', 'delete',)

    def get_serializer_class(self):
        if self.action in {'create', 'partial_update'}:
            return RecipeWriteSerializer
        return RecipeReadSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Performs all operations with tags.
    Handles all requests for the api/v1/tags/ endpoint."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


# class RecipeListViewSet(viewsets.ModelViewSet):
#     """Performs all operations with tags.
#     Handles all requests for the api/v1/tags/ endpoint."""

# class UserViewSet(viewsets.ModelViewSet):
#     pass