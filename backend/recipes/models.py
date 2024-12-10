from django.contrib.auth import get_user_model
from django.db import models

from users.models import User


class Ingredient(models.Model):
    """Модель ингридиента."""
    name = models.TextField('Название')
    unit_of_measurement = models.TextField('Единица измерения')

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Модель тэга."""
    name = models.TextField('Название')
    slug = models.SlugField('Слаг', unique=True, max_length=50)


class Recipe(models.Model):
    """Модель отзыва."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
    )
    title = models.TextField('Название')
    image = models.ImageField(
        upload_to='recipes/images/',
        null=True,
        default=None,
        verbose_name='Картинка',
    )
    description = models.TextField('Описание')
    ingredient = models.ManyToManyField(Ingredient, verbose_name='Ингридиент')
    tag = models.ManyToManyField(Tag, verbose_name='Тэг')
    cooking_time = models.PositiveIntegerField('Время приготовления')

    def __str__(self):
        return f'{self.title} {self.author}'
