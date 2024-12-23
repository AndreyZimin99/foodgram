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


class RecipeIngredient(models.Model):
    name = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()
    measurement_unit = models.TextField('Единица измерения')

    def __str__(self):
        return f'{self.name}'


class Recipe(models.Model):
    """Модель отзыва."""

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
    cooking_time = models.PositiveIntegerField('Время приготовления')
    is_favorited = models.BooleanField(default=False, verbose_name='Избранное')
    is_in_shopping_cart = models.BooleanField(default=False,
                                              verbose_name='Список покупок')

    def __str__(self):
        return f'{self.name} {self.author}'


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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_recipe'
            )
        ]

    def __str__(self):
        return f"Shopping List {self.id}"


class ShortLink(models.Model):
    recipe_id = models.PositiveIntegerField(unique=True)
    short_link = models.CharField(max_length=255)

    def __str__(self):
        return self.short_link
