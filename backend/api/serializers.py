import base64
import re
import logging

from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (Recipe, RecipeIngredient, ShoppingCart,
                            Tag, Ingredient, Favorite, ShortLink)
from users.models import Subscription, User


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
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
            'is_subscribed',
            'avatar',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(
                user=request.user, subscribing=obj).exists()
        return False


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
    id = serializers.IntegerField()

    class Meta:
        fields = ['id', 'amount']
        model = RecipeIngredient


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    name = serializers.SlugRelatedField(
        slug_field='name', read_only=True
    )

    class Meta:
        fields = ['id', 'name', 'measurement_unit', 'amount']
        model = RecipeIngredient


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецепта."""

    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )
    ingredients = RecipeIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = [
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'name',
            'image',
            'text',
            'cooking_time',
            'is_in_shopping_cart',
        ]
        model = Recipe

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data.pop('id')
            ingredient = Ingredient.objects.get(id=ingredient_id)
            amount = ingredient_data.pop('amount')
            recipe_ingredient = RecipeIngredient.objects.create(
                name=ingredient,
                amount=amount,
                measurement_unit=ingredient.measurement_unit
            )

            recipe.ingredients.add(recipe_ingredient)
        recipe.tags.set(tags_data)
        return recipe

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        ingredients_lst = []
        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data.pop('id')
            ingredient = Ingredient.objects.get(id=ingredient_id)
            amount = ingredient_data.pop('amount')
            recipe_ingredient = RecipeIngredient.objects.create(
                name=ingredient,
                amount=amount,
                measurement_unit=ingredient.measurement_unit
            )

            ingredients_lst.append(recipe_ingredient)

        instance.ingredients.set(ingredients_lst)
        instance.tags.set(tags_data)
        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['author'] = UserSerializer(instance.author).data
        representation['tags'] = TagSerializer(instance.tags.all(),
                                               many=True).data
        representation['ingredients'] = IngredientInRecipeSerializer(
            instance.ingredients.all(),
            many=True).data
        return representation

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return Favorite.objects.filter(
                user=request.user, recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return ShoppingCart.objects.filter(
                user=request.user, recipe=obj).exists()
        return False


class RecipeLessFieldsSerializer(serializers.ModelSerializer):

    class Meta:
        fields = [
            'id',
            'name',
            'image',
            'cooking_time',
        ]
        model = Recipe


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    recipe = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True,
        default=None
    )

    class Meta:
        model = Favorite
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe')
            )
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation = RecipeLessFieldsSerializer(instance.recipe).data
        return representation


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
    )

    class Meta:
        model = Subscription
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'subscribing')
            )
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation = UserSerializer(instance.subscribing).data
        recipes_limit = self.context.get('recipes_limit', None)
        if recipes_limit:
            representation['recipes'] = RecipeSerializer(
                Recipe.objects.filter(
                    author=instance.subscribing)[:recipes_limit],
                many=True
            ).data
        else:
            representation['recipes'] = RecipeSerializer(
                Recipe.objects.filter(
                    author=instance.subscribing),
                many=True
            ).data
        representation['recipes_count'] = Recipe.objects.filter(
            author=instance.subscribing).count()
        return representation


class SubscriptionListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = ['user']


class ShoppingCartSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    recipe = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True,
        default=None
    )

    class Meta:
        model = ShoppingCart
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe')
            )
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation = RecipeLessFieldsSerializer(instance.recipe).data
        return representation


class ShortLinkSerializer(serializers.Serializer):
    short_link = serializers.CharField()

    class Meta:
        model = ShortLink
        fields = 'short_link'
