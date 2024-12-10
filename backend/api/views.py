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


from recipes.models import Recipe, Tag, Ingredient
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


# class UserMeView(APIView):
#     permission_classes = [IsAuthenticated()]

#     def get(self, request):
#         serializer = UserSerializer(request.user)
#         return Response(serializer.data)

        # пока без этого
    # @action(
    #     detail=False,
    #     methods=['get', 'put', 'post', 'delete'],
    #     url_path='me'
    # )
    # def me(self, request):
    #     """Получение или изменение данных текущего пользователя."""
    #     if request.method == 'GET':
    #         user_data = self.get_serializer(request.user).data
    #         return Response(user_data)
           

        #    Пока для информации
        # if request.method == 'PUT':
        #     serializer = 
        #     return Response(user_data)
        
        # if request.method == 'PATCH':
        #     serializer = self.get_serializer(
        #         request.user, data=request.data, partial=True
        #     )
        #     serializer.is_valid(raise_exception=True)
        #     serializer.save()
        #     return Response(serializer.data)

        # if request.method == 'DELETE':
        #     return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = PageNumberPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


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
