from django.conf import settings
from rest_framework.pagination import PageNumberPagination


class FoodgramPagination(PageNumberPagination):
    """Отображает по 6 объектов ответа на странице."""

    page_size_query_param = 'limit'
    page_size = settings.NUMBER_OF_RECIPES
