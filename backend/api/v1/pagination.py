from rest_framework.pagination import LimitOffsetPagination


class FoodgramPagination(LimitOffsetPagination):
    """Отображает по 6 объектов ответа на странице."""

    limit_query_param = 'limit'
    page_size = 6
