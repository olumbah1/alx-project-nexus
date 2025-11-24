from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.tokens import PasswordResetTokenGenerator, default_token_generator
from .tasks import send_verification_email_task, send_password_reset_email_task

token_generator = PasswordResetTokenGenerator()


def send_verification_email(user):
    """
    Trigger async task to send email verification link.
    """
    # Call Celery task asynchronously with user ID (UUID as string)
    send_verification_email_task.delay(str(user.id))


def send_password_reset_email(user):
    """
    Trigger async task to send password reset email.
    """
    # Call Celery task asynchronously with user ID (UUID as string)
    send_password_reset_email_task.delay(str(user.id))


def make_password_reset_email(user):
    """
    Build uid and token for reset link and return (uid, token, url)
    Works with UUID primary key.
    """
    uid = str(user.id)
    token = token_generator.make_token(user)
    frontend_base = getattr(settings, 'FRONTEND_PASSWORD_RESET_URL', None)
    if frontend_base:
        reset_url = f"{frontend_base}?uid={uid}&token={token}"
    else:
        reset_url = f"uid={uid}&token={token}"
    return uid, token, reset_url