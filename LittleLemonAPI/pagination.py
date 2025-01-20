from rest_framework import pagination

class MenuItemListPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'per_page'
    max_page_size = 50
    page_query_param = 'page'