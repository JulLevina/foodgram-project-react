from rest_framework.pagination import PageNumberPagination


class FoodgramPagination(PageNumberPagination):
    limit_query_param = 'limit'
    page_size = 6
