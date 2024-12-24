from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, mixins, status, viewsets
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
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
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    ShoppingCart,
    ShortLink,
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
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'delete', 'patch']

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
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class SubcribtionCreateDestroyViewSet(
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
        if user == subscribing:
            raise ValidationError(
                'Вы не можете подписаться на себя.'
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

    def get_context_data(self, request, *args, **kwargs):
        recipes_limit = request.query_params.get('recipes_limit', None)
        response = self.retrieve(request, *args, **kwargs)

        response.data['recipes'] = SubscriptionSerializer(
            response.data,
            context={'recipes_limit': recipes_limit}
        ).data['recipes']
        return response


class SubscriptionListViewSet(mixins.ListModelMixin, viewsets.ViewSet):
    """Получение списка подписок."""
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def list(self, request):
        subscriptions = Subscription.objects.filter(user=request.user)
        paginator = self.pagination_class()
        paginated_subscriptions = paginator.paginate_queryset(subscriptions,
                                                              request)
        serializer = SubscriptionSerializer(paginated_subscriptions, many=True)
        return paginator.get_paginated_response(serializer.data)


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

    from django.http import HttpResponse

    def download_txt(self, request):
        shopping_carts = ShoppingCart.objects.filter(user=request.user)
        recipes = []
        for shopping_cart in shopping_carts:
            recipes.append(shopping_cart.recipe)

        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = 'attachment; \
                                           filename="shopping_cart.txt"'

        content = 'Shopping_cart\n'
        ingredients = []
        for recipe in recipes:
            for ingredient in recipe.ingredients.all():
                ingredients.append(ingredient)

        combined_ingredients = {}
        for ingredient in ingredients:
            name = ingredient.name.name
            amount = ingredient.amount
            if name in combined_ingredients:
                combined_ingredients[name]['amount'] += amount
            else:
                combined_ingredients[name] = {
                    'name': name,
                    'measurement_unit': ingredient.measurement_unit,
                    'amount': amount
                }
        ingredient_list = list(combined_ingredients.values())
        for ingredient in ingredient_list:
            ingredient_data = f'{ingredient["name"]} \
({ingredient["measurement_unit"]}) - {ingredient["amount"]} '
            content += ingredient_data + '\n'

        response.write(content)
        return response


class RecipeGetLinkView(generics.GenericAPIView):
    """Класс для получения короткой ссылки для рецепта."""
    def get(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)

        short_link, created = ShortLink.objects.get_or_create(recipe=recipe)

        return Response({
            "short-link": short_link.get_short_link()
        })


class RedirectShortLinkView(generics.GenericAPIView):
    """Класс для переадресации по короткой ссылке."""
    def get(self, request, short_code):
        short_link = get_object_or_404(ShortLink, short_code=short_code)
        return redirect(
            f"https://fgm.hopto.org/recipes/{short_link.recipe.id}/"
        )
