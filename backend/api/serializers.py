import base64
import re
import logging

from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import Recipe, RecipeIngredient, Tag, Ingredient
from subscriptions.models import Subscribtion
from users.models import User


logger = logging.getLogger(__name__)
MAX_EMAIL_LENGTH = 254
MAX_USERNAME_LENGTH = 150


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class UserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя."""

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )

    def validate_username(self, value):
        """Проверка имени пользователя."""
        if value.lower() == 'me':
            raise serializers.ValidationError('Недопустимое имя пользователя')
        if not re.match(r'^[\w.@+-]+$', value):
            raise serializers.ValidationError(
                'Имя пользователя содержит недопустимые символы'
            )
        return value


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя."""

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
            'avatar'
        )


class TokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена."""

    email = serializers.CharField(
        max_length=MAX_USERNAME_LENGTH, required=True
    )
    password = serializers.CharField(required=True)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингридиента."""

    class Meta:
        fields = '__all__'
        model = Ingredient


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тэга."""

    class Meta:
        fields = '__all__'
        model = Tag


class RecipeIngredientSerializer(serializers.ModelSerializer):
    # id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    # amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        fields = ['id']  #, 'amount']
        model = RecipeIngredient


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецепта."""

    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )
    ingredients = RecipeIngredientSerializer(many=True)
    # tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
    #                                           many=True)

    image = Base64ImageField()
    image_url = serializers.SerializerMethodField(
        'get_image_url',
        read_only=True,
    )

    class Meta:
        fields = '__all__'
        model = Recipe

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient_data in ingredients_data:
            print(f'ing_data {ingredient_data}')
            ingredient = ingredient_data.pop('id')
            # ingredient = Ingredient.objects.get(id=ingredient_data)
            RecipeIngredient.objects.create(recipe=recipe, ingredient=ingredient)

        return recipe

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None


class SubscriptionSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    subscribing = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
        # queryset=User.objects.all()
    )

    class Meta:
        model = Subscribtion
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Subscribtion.objects.all(),
                fields=('user', 'subscribing')
            )
        ]

    # def validate_subscribing(self, value):
    #     subscriber = self.context['request'].user
    #     subscribing = value
    #     if not User.objects.filter(username=subscribing).exists():
    #         raise serializers.ValidationError(
    #             'Пользователь с таким именем не найден.')
    #     if subscriber == subscribing:
    #         raise serializers.ValidationError(
    #             'Вы не можете подпитсаться на себя.')
    #     return subscribing
