from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail

CONFIRMATION_SUBJECT = 'Код подтверждения'
CONFIRMATION_MESSAGE = 'Ваш код подтверждения: {}'


class EmailConfirmationMixin:
    """Миксин для отправки кода подтверждения на почту."""

    @staticmethod
    def send_confirmation_code(user):
        """Формирует и отправляет подтверждение (confirmation_code)."""
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            CONFIRMATION_SUBJECT,
            CONFIRMATION_MESSAGE.format(confirmation_code),
            settings.SENDER_EMAIL,
            [user.email],
            fail_silently=False,
        )
