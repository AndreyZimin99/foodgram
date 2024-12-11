from django.contrib.auth import get_user_model
from django.db import models

from users.models import User


class Ingredient(models.Model):
    """Модель ингридиента."""
    name = models.TextField('Название')
    measurement_unit = models.TextField('Единица измерения')

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Модель тэга."""
    name = models.TextField('Название')
    slug = models.SlugField('Слаг', unique=True, max_length=50)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель отзыва."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
    )
    name = models.TextField('Название') # исправить на name
    image = models.ImageField(
        upload_to='recipes/images/',
        null=True,
        default=None,
        verbose_name='Картинка',
    )
    text = models.TextField('Описание')
    ingredients = models.ManyToManyField(Ingredient,
                                         verbose_name='Ингредиенты',
                                         through='RecipeIngredient')
    tags = models.ManyToManyField(Tag, verbose_name='Тэги')
    cooking_time = models.PositiveIntegerField('Время приготовления')

    def __str__(self):
        return f'{self.name} {self.author}'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.FloatField()

    def __str__(self):
        return f'{self.recipe} {self.ingredient}'
