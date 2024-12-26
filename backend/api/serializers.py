import base64
import re

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.validators import MinValueValidator
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (Favorite, Ingredient, RecipeIngredient, Recipe,
                            ShoppingCart, Tag)
from users.models import Subscription, User


def get_is(self, obj):
    request = self.context.get('request')
    if request and request.user.is_authenticated:
        return obj.filter(
            user=request.user).exists()
    return False


def recipe_ingredient_create(self, validated_data):
    ingredients_data = validated_data.pop('ingredients')
    recipe_ingredients = []
    for ingredient_data in ingredients_data:
        ingredient = ingredient_data.pop('id')
        amount = ingredient_data.pop('amount')
        recipe_ingredient = RecipeIngredient(
            name=ingredient,
            amount=amount,
            measurement_unit=ingredient.measurement_unit
        )
        recipe_ingredients.append(recipe_ingredient)
    created_ingredients = RecipeIngredient.objects.bulk_create(
        recipe_ingredients)
    return [ingredient.id for ingredient in created_ingredients]


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class UserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания пользователя."""

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
        if not re.match(settings.USERNAME_REGEX, value):
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
        return get_is(self, obj.subscribing)


class TokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена."""

    email = serializers.CharField(
        max_length=settings.MAX_USERNAME_LENGTH, required=True
    )
    password = serializers.CharField(required=True)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиента."""

    class Meta:
        fields = '__all__'
        model = Ingredient


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тэга."""

    class Meta:
        fields = '__all__'
        model = Tag


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления ингредиента в рецпт."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(
        validators=[MinValueValidator(settings.MIN_VALUE)])

    class Meta:
        fields = ['id', 'amount']
        model = RecipeIngredient


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор отображения ингредиента внутри рецпта."""
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
    cooking_time = serializers.IntegerField(
        validators=[MinValueValidator(settings.MIN_VALUE)])

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
        tags_data = validated_data.pop('tags')
        ingredient_ids = recipe_ingredient_create(self, validated_data)
        recipe = Recipe.objects.create(**validated_data)
        recipe.ingredients.set(ingredient_ids)
        recipe.tags.set(tags_data)
        return recipe

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags')
        ingredient_ids = recipe_ingredient_create(self, validated_data)
        instance.ingredients.set(ingredient_ids)
        instance.tags.set(tags_data)
        instance.save()
        super().update(instance, validated_data)
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
        return get_is(self, obj.favorites)

    def get_is_in_shopping_cart(self, obj):
        return get_is(self, obj.shoppingcart)


class RecipeLessFieldsSerializer(serializers.ModelSerializer):
    """Сериализатор рецепта с меньшим числом полей."""

    class Meta:
        fields = [
            'id',
            'name',
            'image',
            'cooking_time',
        ]
        model = Recipe


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор избранного."""
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
        representation = RecipeLessFieldsSerializer(instance.recipe).data
        return representation


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор подписки."""
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
    recipes_count = serializers.ReadOnlyField(
        source='subscribing.recipes.count',
    )

    class Meta:
        model = Subscription
        fields = ['user', 'subscribing', 'recipes_count']
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'subscribing')
            )
        ]

    def validate_subscribing(self, value):
        user = self.context['request'].user
        subscribing = value
        if not User.objects.filter(username=subscribing).exists():
            raise serializers.ValidationError(
                'Пользователь с таким именем не найден.')
        if user == subscribing:
            raise serializers.ValidationError(
                'Вы не можете подписаться на себя.')
        return value

    def to_representation(self, instance):
        representation = UserSerializer(instance.subscribing).data
        recipes_limit = self.context.get('recipes_limit', None)
        if recipes_limit:
            representation['recipes'] = RecipeSerializer(
                instance.subscribing.recipes.all()[:recipes_limit],
                many=True
            ).data
        else:
            representation['recipes'] = RecipeLessFieldsSerializer(
                instance.subscribing.recipes.all(),
                many=True
            ).data
        data = super().to_representation(instance)
        representation.update(data)
        representation.pop('user', None)
        representation.pop('subscribing', None)
        return representation


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор списка покупок."""
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
