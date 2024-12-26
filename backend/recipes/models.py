from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator
from django.utils.crypto import get_random_string

from users.models import User


class Ingredient(models.Model):
    """Модель ингредиента."""
    name = models.TextField('Название', unique=True)
    measurement_unit = models.TextField('Единица измерения')

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Модель тэга."""
    name = models.TextField('Название', unique=True)
    slug = models.SlugField('Слаг',
                            unique=True,
                            max_length=settings.MAX_LENGTH)

    class Meta:
        verbose_name = 'тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Модель ингредиента внутри рецепта."""
    name = models.ForeignKey(Ingredient,
                             on_delete=models.CASCADE,
                             verbose_name='Ингредиент')
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(settings.MIN_VALUE)],
        verbose_name='Количество'
    )
    measurement_unit = models.TextField('Единица измерения')

    class Meta:
        verbose_name = 'ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'

    def __str__(self):
        return f'{self.name}'


class Recipe(models.Model):
    """Модель рецепта."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
    )
    name = models.TextField('Название рецепта')
    image = models.ImageField(
        upload_to='recipes/images/',
        null=True,
        default=None,
        verbose_name='Картинка',
    )
    text = models.TextField('Описание')
    ingredients = models.ManyToManyField(RecipeIngredient,
                                         verbose_name='Ингредиенты',
                                         blank=False)
    tags = models.ManyToManyField(Tag, verbose_name='Тэги', blank=False)
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(settings.MIN_VALUE)],
        verbose_name='Время приготовления'
    )
    is_favorited = models.BooleanField(default=False,
                                       verbose_name='Избранное')
    is_in_shopping_cart = models.BooleanField(default=False,
                                              verbose_name='Список покупок')

    class Meta:
        default_related_name = 'recipes'
        ordering = ('-id',)
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.name} {self.author}'


class Favorite(models.Model):
    """Модель избранного."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        default_related_name = 'favorites'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]
        verbose_name = 'избранное'
        verbose_name_plural = 'Избранное'


class ShoppingCart(models.Model):
    """Модель списка покупок."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        default_related_name = 'shoppingcart'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_sc'
            )
        ]
        verbose_name = 'список покупок'
        verbose_name_plural = 'Список покупок'


class ShortLink(models.Model):
    """Модель коротких ссылок."""
    recipe = models.OneToOneField('Recipe', on_delete=models.CASCADE)
    short_code = models.CharField(
        max_length=4,
        unique=True,
        default=get_random_string(length=4)
    )

    def get_short_link(self):
        return f"https://fgm.hopto.org/s/{self.short_code}"

    class Meta:
        verbose_name = 'короткая ссылка'
        verbose_name_plural = 'Короткие ссылки'
