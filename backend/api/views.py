from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, views, viewsets
# from rest_framework import filters, mixins, permissions, viewsets
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView


from recipes.models import Recipe, RecipeIngredient, Tag, Ingredient
from subscriptions.models import Subscribtion
from users.models import User
# from .mixins import EmailConfirmationMixin
from .pagination import UserPagination
from .permissions import IsAdmin, IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (
    RecipeSerializer,
    TagSerializer,
    IngredientSerializer,
    SubscriptionSerializer,
    # SignupSerializer,
    TokenSerializer,
    UserSerializer,
    UserCreateSerializer,
)


# class CreateListViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
#                         viewsets.GenericViewSet):
#     pass


class CreateRetrieveListDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):

    pass


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
            # token = default_token_generator.make_token(user)
            token, created = Token.objects.get_or_create(user=user)
            return Response(
                {'auth_token': token.key}, status=status.HTTP_200_OK
            )

        return Response(
            {'error': 'Неверный пароль'},
            status=status.HTTP_400_BAD_REQUEST,
        )


class UserViewSet(viewsets.ModelViewSet):
    """Класс для работы с пользователями."""

    queryset = User.objects.all()
    # serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    # lookup_field = 'username'
    pagination_class = UserPagination
    filter_backends = [SearchFilter]
    search_fields = ['username']
    http_method_names = ['post', 'get']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        if self.action == 'create':
            return [AllowAny()]
        return super().get_permissions()

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
    permission_classes = [IsAuthenticated]

    def put(self, request):
        request.user.avatar = request.data['avatar']
        request.user.save()
        return Response(request.data)

    def delete(self, request):
        request.user.avatar.delete(save=False)
        request.user.avatar = None
        request.user.save()
        return Response({'detail': 'Учетные данные не были предоставлены.'})


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = PageNumberPagination

    # def get_queryset(self):
    #     return (
    #         Recipe.objects.all()
    #         .prefetch_related('ingredients')
    #         .prefetch_related('tags')
    #     )

    def perform_create(self, serializer):
        # ingredients_data = self.validated_data.pop('ingredients')
        # recipe = Recipe.objects.create(**self.validated_data)
        # # ingredients = self.request.data['ingredients']
        # for item in ingredients_data:
        #     ingredient_id = item['id']
        #     amount = item['amount']
        #     ingredient = Ingredient.objects.get(id=ingredient_id)
        #     ingredients = RecipeIngredient.objects.create(
        #         recipe=recipe, ingredient=ingredient, amount=amount)
        serializer.save(author=self.request.user)  # ingredients=ingredients)

    # def create(self, validated_data):
    #     ingredients_data = validated_data.pop('ingredients')
    #     recipe = Recipe.objects.create(**validated_data)

    #     for item in ingredients_data:
    #         ingredient_id = item['id']
    #         quantity = item['quantity']
    #         ingredient = Ingredient.objects.get(id=ingredient_id)
    #         RecipeIngredient.objects.create(recipe=recipe, ingredient=ingredient, quantity=quantity)

    #     return recipe


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    # pagination_class = PageNumberPagination


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    # pagination_class = PageNumberPagination


# class SubcribtionViewSet(CreateListViewSet):
class SubcribtionViewSet(CreateRetrieveListDestroyViewSet):
    queryset = Subscribtion.objects.all()
    serializer_class = SubscriptionSerializer
    # filter_backends = [SearchFilter]
    # http_method_names = ['post', 'get', 'delete']
    # search_fields = ('subscribing__username',)

    def perform_create(self, serializer):
        user = self.request.user
        subscribing = get_object_or_404(
            User,
            id=self.kwargs['user_id'],
        )
        serializer.save(user=user, subscribing=subscribing)

    def delete(self, request, *args, **kwargs):
        user = self.request.user
        subscribing = get_object_or_404(
            User,
            id=self.kwargs['user_id'],
        )
        instance = get_object_or_404(
            Subscribtion,
            user=user,
            subscribing=subscribing
        )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
