from django.contrib.auth.models import AbstractUser
from django.core import validators
from django.db import models


class User(AbstractUser):
    '''Модель пользователя.'''

    email = models.EmailField(unique=True)
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[validators.RegexValidator(r'^[\w.@+-]+$')],
    )
    first_name = models.CharField(max_length=150, blank=False, null=False)
    last_name = models.CharField(max_length=150, blank=False, null=False)
    password = models.CharField(max_length=150, blank=False, null=False)
    avatar = models.ImageField(
        upload_to='users/images/',
        null=True,
        default=None
    )

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_staff or self.is_superuser

    def __str__(self):
        return self.username
