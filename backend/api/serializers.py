import re

from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import Recipe, Tag, Ingredient
from subscriptions.models import Subscribtion
from users.models import User


MAX_EMAIL_LENGTH = 254
MAX_USERNAME_LENGTH = 150


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


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецепта."""

    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )
    tag = serializers.SlugRelatedField(
        queryset=Tag.objects.all(), slug_field='slug', many=True
    )
    ingredient = serializers.SlugRelatedField(
        queryset=Ingredient.objects.all(), slug_field='slug', many=True
    )

    class Meta:
        fields = '__all__'
        model = Recipe


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
