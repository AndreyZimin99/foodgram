from django.conf import settings
from rest_framework.pagination import LimitOffsetPagination


class CustomPagination(LimitOffsetPagination):
    """Пагинация для UserViewSet."""

    default_limit = settings.POST_PER_PAGE
    max_limit = 100
