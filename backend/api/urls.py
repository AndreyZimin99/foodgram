from django.urls import include, path
from rest_framework import routers

from api.views import (
    FavoriteViewSet,
    IngredientViewSet,
    Logout,
    RecipeGetLinkView,
    RecipeViewSet,
    ShoppingCartViewSet,
    SubscribtionCreateDestroyViewSet,
    SubscriptionListViewSet,
    TagViewSet,
    TokenViewSet,
    UserAvatarView,
    UserMeView,
    UserPasswordView,
    UserViewSet,
)

router_v1 = routers.DefaultRouter()
router_v1.register('users', UserViewSet, basename='users')
router_v1.register('recipes', RecipeViewSet, basename='recipes')
router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('auth/token/login/', TokenViewSet.as_view(), name='login'),
    path('auth/token/logout/', Logout.as_view(), name='logout'),
    path('users/me/', UserMeView.as_view(), name='user-me'),
    path('users/me/avatar/', UserAvatarView.as_view(), name='user-avatar'),
    path('users/set_password/',
         UserPasswordView.as_view(),
         name='user-password'),
    path(
        'users/<int:user_id>/subscribe/',
        SubscribtionCreateDestroyViewSet.as_view(
            {'post': 'create', 'delete': 'destroy'}
        ),
        name='subcribe'
    ),
    path('users/subscriptions/',
         SubscriptionListViewSet.as_view({'get': 'list'}),
         name='subcriptions'),
    path(
        'recipes/<int:recipe_id>/favorite/',
        FavoriteViewSet.as_view(
            {'post': 'create', 'delete': 'destroy'}
        ),
        name='favorite'
    ),
    path(
        'recipes/<int:recipe_id>/shopping_cart/',
        ShoppingCartViewSet.as_view(
            {'post': 'create', 'delete': 'destroy'}
        ),
        name='shopping_cart'
    ),
    path('recipes/download_shopping_cart/',
         ShoppingCartViewSet.as_view({'get': 'download_txt'})),
    path('recipes/<int:recipe_id>/get-link/',
         RecipeGetLinkView.as_view(), name='short-link'),
    path('', include(router_v1.urls)),
]
