from django.conf import settings
from rest_framework.pagination import (LimitOffsetPagination,
                                       PageNumberPagination)


class UserPagination(LimitOffsetPagination):
    """Пагинация для UserViewSet."""

    default_limit = settings.POST_PER_PAGE
    # page_size_query_param = 'page_size'
    max_limit = 100
