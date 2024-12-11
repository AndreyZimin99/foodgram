from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework import routers
from rest_framework.authtoken import views

from api.views import (
    RecipeViewSet,
    SubcribtionViewSet,
    # SignupViewSet,
    TagViewSet,
    TokenViewSet,
    IngredientViewSet,
    UserViewSet,
    UserMeView,
    UserAvatarView,
)

router_v1 = routers.DefaultRouter()
router_v1.register('users', UserViewSet, basename='users')
router_v1.register('recipes', RecipeViewSet, basename='recipes')
router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')
router_v1.register('subscribe', SubcribtionViewSet, basename='subscribe')

urlpatterns = [
    path('auth/token/login/', TokenViewSet.as_view(), name='token'),
    path('', include(router_v1.urls)),
    path('users/<int:user_id>/', include(router_v1.urls)),
    path('users/me/', UserMeView.as_view(), name='user-me'),
    path('users/me/avatar/', UserAvatarView.as_view(), name='user-avatar'),
    # path('users/me/avatar', UserViewSet.as_view({'put': 'me'}, name='avatar'),
    # path('users/me/password', UserViewSet.as_view({'post': 'me', 'delete': 'me'}, name='password'),
]

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL,
#                           document_root=settings.MEDIA_ROOT)
