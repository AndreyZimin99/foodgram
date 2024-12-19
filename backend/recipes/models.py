from django.contrib.auth import get_user_model
from django.db import models

from users.models import User


class Ingredient(models.Model):
    """Модель ингридиента."""
    name = models.TextField('Название')
    measurement_unit = models.TextField('Единица измерения')
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True,
                                 null=True, default=None)

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
    is_favorite = models.BooleanField(default=False, verbose_name='Избранное')

    def __str__(self):
        return f'{self.name} {self.author}'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    # amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.recipe} {self.ingredient}'


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]


class ShoppingCart(models.Model):
    ingredients = models.ManyToManyField(Ingredient)

    def __str__(self):
        return f"Shopping List {self.id}"
