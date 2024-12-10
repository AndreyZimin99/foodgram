from django.db import models

from users.models import User


class Subscribtion(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscribers')
    subscribing = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribing'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'subscribing'],
                name='unique_subcribe'
            )
        ]
