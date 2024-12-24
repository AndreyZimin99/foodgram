from django.contrib.auth.models import AbstractUser
from django.core import validators
from django.db import models


class User(AbstractUser):
    """Модель пользователя."""

    email = models.EmailField(unique=True, verbose_name='Почта')
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[validators.RegexValidator(r'^[\w.@+-]+$')],
        verbose_name='Имя пользователя',
    )
    first_name = models.CharField(max_length=150, blank=False, null=False,
                                  verbose_name='Имя')
    last_name = models.CharField(max_length=150, blank=False, null=False,
                                 verbose_name='Фамилия')
    password = models.CharField(max_length=150, blank=False, null=False,
                                verbose_name='Пароль')
    avatar = models.ImageField(
        upload_to='users/images/',
        null=True,
        default=None,
        verbose_name='Аватар'
    )
    is_subscribed = models.BooleanField(default=False, verbose_name='Подписка')

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Модель подписок."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Подписчик'
    )
    subscribing = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribing',
        verbose_name='Автор'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'subscribing'],
                name='unique_subcribe'
            )
        ]
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'
