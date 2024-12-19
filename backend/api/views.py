from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, views, viewsets
# from rest_framework import filters, mixins, permissions, viewsets
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import (LimitOffsetPagination,
                                       PageNumberPagination)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from recipes.models import Favorite, Recipe, RecipeIngredient, ShoppingCart, Tag, Ingredient
from users.models import Subscribtion, User
# from .mixins import EmailConfirmationMixin
from api.pagination import UserPagination
from api.permissions import IsAdmin, IsAdminOrReadOnly, IsAuthorOrReadOnly
from api.serializers import (
    FavoriteSerializer,
    RecipeSerializer,
    TagSerializer,
    IngredientSerializer,
    ShoppingCartSerializer,
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


class Logout(APIView):
    """Класс для удаления токена."""
    def post(self, request, format=None):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


    # def delete(self, request):
    #     """Удаление токена."""
    #     token = get_object_or_404(Token, user=request.user)
    #     token.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)

        # email = serializer.validated_data['email']
        # password = serializer.validated_data['password']
        # user = get_object_or_404(User, email=email)
        # if password == user.password:
        #     # token = default_token_generator.make_token(user)
        #     token, created = Token.objects.get_or_create(user=user)
        #     return Response(
        #         {'auth_token': token.key}, status=status.HTTP_200_OK
        #     )

        # return Response(
        #     {'error': 'Неверный пароль'},
        #     status=status.HTTP_400_BAD_REQUEST,
        # )


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """Класс для работы с пользователями."""

    queryset = User.objects.all()
    # serializer_class = UserSerializer
    # permission_classes = [IsAuthenticated]
    # lookup_field = 'username'
    pagination_class = UserPagination
    # filter_backends = [SearchFilter]
    # search_fields = ['username']
    # pagination_class = LimitOffsetPagination

    # def get_permissions(self):
    #     if self.action in ['list', 'retrieve']:
    #         return [IsAuthenticated()]
    #     if self.action == 'create':
    #         return [AllowAny()]
    #     return super().get_permissions()

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
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = PageNumberPagination
    pagination_class.page_size = settings.POST_PER_PAGE

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        if self.action in ['update', 'destroy']:
            return [IsAuthorOrReadOnly()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    # @action(detail=True, methods=['post'], url_path='shopping_cart')
    # def add_to_shopping_list(self, request, pk=None):
    #     recipe = get_object_or_404(Recipe, id=pk)
    #     # shopping_list = [{"name": ingredient.name, "amount": ingredient.amount, "measurement_unit": ingredient.measurement_unit}
    #     #                  for ingredient in recipe.ingredients.all()]
    #     shopping_list = [ingredient for ingredient in recipe.ingredients.all()]
    #     return Response(shopping_list, status=status.HTTP_201_CREATED)


class TagViewSet(
    # mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    # mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    # permission_classes = [AllowAny]
    # pagination_class = PageNumberPagination

    # def get_permissions(self):
    #     if self.action in ['create', 'destroy']:
    #         return [IsAdmin()]
    #     return super().get_permissions()


class IngredientViewSet(
    # mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    # mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    # permission_classes = [AllowAny]
    # pagination_class = PageNumberPagination

    # def get_permissions(self):
    #     if self.action in ['create', 'destroy']:
    #         return [IsAdmin()]
    #     return super().get_permissions()


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
        try:
            user = request.user
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
        except Subscribtion.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class FavoriteViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = [IsAuthenticated]
    serializer_class = FavoriteSerializer

    def perform_create(self, serializer):
        user = self.request.user
        recipe = get_object_or_404(
            Recipe,
            id=self.kwargs['recipe_id'],
        )
        serializer.save(user=user, recipe=recipe)

    def destroy(self, request):
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


# def generate_pdf(request, recipe_id):
#     recipe = Recipe.objects.get(id=recipe_id)
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = f'attachment; filename="{recipe.title}.pdf"'

#     p = canvas.Canvas(response, pagesize=letter)
#     p.drawString(100, 750, f"Recipe: {recipe.title}")

#     y_position = 730
#     for ingredient in recipe.ingredients.all():
#         p.drawString(100, y_position, f"{ingredient.quantity} {ingredient.unit} of {ingredient.name}")
#         y_position -= 20

#     p.showPage()
#     p.save()
#     return response

class ShoppingCartViewSet(viewsets.ModelViewSet):
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer
    permission_classes = [IsAuthenticated]

    def add_ingredients(self, request, recipe_id):
        serializer = self.get_serializer(data=request.data)
        recipe = Recipe.objects.get(id=recipe_id)
        shopping_list = ShoppingCart.objects.create()
        shopping_list.ingredients.set(recipe.ingredients.all())
        shopping_list.save()
        serializer = ShoppingCartSerializer(shopping_list)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # def download_pdf(self, request):
    #     shoppings_cart = ShoppingCart.objects.all()
    #     print(f'shopping_cart {shoppings_cart}')
    #     response = HttpResponse(content_type='application/pdf')
    #     response['Content-Disposition'] = 'attachment; filename="shopping_cart.pdf"'

    #     p = canvas.Canvas(response, pagesize=letter)
    #     # p.drawString(100, 750, f"Shopping Cart")
    #     p.setFont('Helvetica', 16)
    #     y_position = 750
    #     for shopping_cart in shoppings_cart:
    #         for ingredient in shopping_cart.ingredients.all():
    #             ing_data = [ingredient.name,
    #                         str(ingredient.amount),
    #                         ingredient.measurement_unit]
    #             p.drawString(100, y_position, ' '.join(ing_data))
    #             y_position -= 20

    #     p.showPage()
    #     p.save()
    #     return response

    from django.http import HttpResponse

    def download_txt(self, request):
        shopping_carts = ShoppingCart.objects.all()

        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="shopping_cart.txt"'

        content = f"Shopping cart\n\n"

        for shopping_cart in shopping_carts:
            for ingredient in shopping_cart.ingredients.all():
                ing_data = f'{ingredient.name} {ingredient.amount} {ingredient.measurement_unit}'
                content += ing_data + "\n"

        response.write(content)

        return response
