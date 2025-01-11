from django.conf import settings
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django_filters import rest_framework as filters
from rest_framework import generics, mixins, status, viewsets
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.filters import SearchFilter
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.filters import RecipeFilter
from api.pagination import CustomPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    FavoriteSerializer,
    IngredientSerializer,
    RecipeSerializer,
    ShoppingCartSerializer,
    SubscriptionSerializer,
    TagSerializer,
    TokenSerializer,
    UserCreateSerializer,
    UserSerializer,
)
from api.utils import create_file_shopping_cart
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from users.models import Subscription, User


class TokenViewSet(ObtainAuthToken):
    """Класс для получения токена."""

    def post(self, request):
        """Обрабатывает получение токена."""
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        user = get_object_or_404(User, email=email)
        if password == user.password:
            token, created = Token.objects.get_or_create(user=user)
            return Response(
                {'auth_token': token.key}, status=status.HTTP_200_OK
            )

        return Response(
            {'error': 'Неверный пароль'},
            status=status.HTTP_400_BAD_REQUEST,
        )


class Logout(APIView):
    """Класс для удаления токена."""
    def post(self, request, format=None):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """Класс для работы с пользователями."""

    queryset = User.objects.all()
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer


class UserMeView(APIView):
    """Получение информации о текущем пользователе."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class UserAvatarView(APIView):
    """Изменение аватара пользователя."""
    permission_classes = [IsAuthenticated]

    def put(self, request):
        request.user.avatar = request.data['avatar']
        request.user.save()
        return Response(request.data)

    def delete(self, request):
        request.user.avatar.delete(save=False)
        request.user.avatar = None
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserPasswordView(APIView):
    """Изменение пароля пользователя."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.password == request.data['current_password']:
            request.user.password = request.data['new_password']
            request.user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'message': 'Введенный пароль не совпадает с текущим'},
                        status=status.HTTP_400_BAD_REQUEST)


class RecipeViewSet(viewsets.ModelViewSet):
    """Класс для работы с рецептами."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = CustomPagination
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'delete', 'patch']

    def get_queryset(self):
        queryset = super().get_queryset()
        page = self.request.query_params.get('page', None)
        if page is not None:
            limit = self.pagination_class.default_limit
            offset = (int(page) - 1) * limit
            self.request.query_params._mutable = True
            self.request.query_params['offset'] = offset
            self.request.query_params['limit'] = limit
            self.request.query_params._mutable = False
        return queryset

    def get_permissions(self):
        if self.request == 'post':
            return [IsAuthenticated()]
        if self.request in ['patch', 'delete']:
            return [IsAuthorOrReadOnly()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class TagViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """Класс для работы с тэгами."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """Класс для работы с ингредиентами."""
    serializer_class = IngredientSerializer

    def get_queryset(self):
        name = self.request.query_params.get('name', '')
        return Ingredient.objects.filter(name__icontains=name)


class SubscribtionCreateDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """Создание и удаление подписки."""
    permission_classes = [IsAuthenticated]
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    pagination_class = CustomPagination

    def perform_create(self, serializer):
        user = self.request.user
        subscribing = get_object_or_404(
            User,
            id=self.kwargs['user_id'],
        )
        serializer.save(user=user, subscribing=subscribing)

    def destroy(self, request, *args, **kwargs):
        try:
            user = request.user
            subscribing = get_object_or_404(
                User,
                id=self.kwargs['user_id'],
            )
            instance = get_object_or_404(
                Subscription,
                user=user,
                subscribing=subscribing
            )
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Subscription.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class SubscriptionListViewSet(viewsets.ModelViewSet):
    """Получение списка подписок."""
    queryset = Subscription.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('user',)
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        page = self.request.query_params.get('page', None)
        if page is not None:
            limit = self.pagination_class.default_limit
            offset = (int(page) - 1) * limit
            self.request.query_params._mutable = True
            self.request.query_params['offset'] = offset
            self.request.query_params['limit'] = limit
            self.request.query_params._mutable = False
        return queryset


class FavoriteViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """Класс для добавления и удаления из избранного."""
    permission_classes = [IsAuthenticated]
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer

    def get_permissions(self):
        if self.request == 'post':
            return [IsAuthenticated()]
        if self.request == 'delete':
            return [IsAuthorOrReadOnly()]
        return super().get_permissions()

    def perform_create(self, serializer):
        user = self.request.user
        recipe = get_object_or_404(
            Recipe,
            id=self.kwargs['recipe_id'],
        )
        serializer.save(user=user, recipe=recipe)

    def destroy(self, request, *args, **kwargs):
        try:
            user = request.user
            recipe = get_object_or_404(
                Recipe,
                id=self.kwargs['recipe_id'],
            )
            favorite = Favorite.objects.get(user=user,
                                            recipe=recipe)
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Favorite.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class ShoppingCartViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """Класс для работы со списком сокупок."""
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request == 'post':
            return [IsAuthenticated()]
        if self.request == 'delete':
            return [IsAuthorOrReadOnly()]
        return super().get_permissions()

    def perform_create(self, serializer):
        user = self.request.user
        recipe = get_object_or_404(
            Recipe,
            id=self.kwargs['recipe_id'],
        )
        serializer.save(user=user, recipe=recipe)

    def destroy(self, request, *args, **kwargs):
        try:
            user = request.user
            recipe = get_object_or_404(
                Recipe,
                id=self.kwargs['recipe_id'],
            )
            shoping_cart = ShoppingCart.objects.get(user=user,
                                                    recipe=recipe)
            shoping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ShoppingCart.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def download_txt(self, request):
        ingredients = (RecipeIngredient.objects
                       .filter(recipes__shoppingcart__user=request.user)
                       .values('name__name', 'measurement_unit')
                       .annotate(total_amount=Sum('amount'))
                       )
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = 'attachment; \
                                           filename="shopping_cart.txt"'
        content = create_file_shopping_cart(ingredients)
        response.write(content)
        return response


class RecipeGetLinkView(generics.GenericAPIView):
    """Класс для получения короткой ссылки для рецепта."""
    def get(self, request, recipe_id):
        try:
            recipe = Recipe.objects.get(id=recipe_id)
            short_link = request.build_absolute_uri(
                f'/s/{recipe.short_link}/')
            return Response({'short-link': short_link})
        except Recipe.DoesNotExist:
            raise NotFound("Рецепт не найден.")


class RedirectShortLinkView(APIView):
    """Класс для переадресации по короткой ссылке."""
    def get(self, request, short_link):
        recipe = get_object_or_404(Recipe, short_link=short_link)
        return redirect(request.build_absolute_uri(
            f'/recipes/{recipe.id}/'))
