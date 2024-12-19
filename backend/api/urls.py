from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework import routers
from rest_framework.authtoken import views

from api.views import (
    FavoriteViewSet,
    Logout,
    RecipeViewSet,
    ShoppingCartViewSet,
    SubcribtionViewSet,
    # SignupViewSet,
    TagViewSet,
    TokenViewSet,
    IngredientViewSet,
    UserPasswordView,
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
router_v1.register('favorite', FavoriteViewSet, basename='favorite')

urlpatterns = [
    path('recipes/download_shopping_cart/', ShoppingCartViewSet.as_view({'get': 'download_txt'})),
    path('auth/token/login/', TokenViewSet.as_view(), name='token'),
    path('auth/token/logout/', Logout.as_view(), name='logout'),
    path('users/me/', UserMeView.as_view(), name='user-me'),
    path('users/me/avatar/', UserAvatarView.as_view(), name='user-avatar'), # users/set_password/
    path('users/set_password/',
         UserPasswordView.as_view(),
         name='user-avatar'),
    path('', include(router_v1.urls)),
    path('users/<int:user_id>/', include(router_v1.urls)),
    path('recipes/<int:recipe_id>/', include(router_v1.urls)),
    path('recipes/<int:recipe_id>/shopping_cart/', ShoppingCartViewSet.as_view({'post': 'add_ingredients'})),
]

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL,
#                           document_root=settings.MEDIA_ROOT)
