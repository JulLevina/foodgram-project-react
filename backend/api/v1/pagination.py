from rest_framework.pagination import PageNumberPagination


class FoodgramPagination(PageNumberPagination):
    """Отображает по 6 объектов ответа на странице."""

    limit_query_param = 'limit'
    page_size = 6
