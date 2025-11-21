from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.tokens import PasswordResetTokenGenerator, default_token_generator
from django.urls import reverse

token_generator = PasswordResetTokenGenerator()


def send_verification_email(user):
    """
    Send email verification link to a user.
    Works with UUID primary key.
    """
    uid = str(user.id)  # UUID as string
    token = default_token_generator.make_token(user)

    verify_url = f"http://localhost:8000/api/auth/verify/{uid}/{token}/"

    message = f"Click the link to verify your email: {verify_url}"

    send_mail(
        "Verify your email",
        message,
        "noreply@yourapp.com",
        [user.email],
        fail_silently=False,
    )


def make_password_reset_email(user):
    """
    Build uid and token for reset link and return (uid, token, url)
    Works with UUID primary key.
    """
    uid = str(user.id)  # UUID as string
    token = token_generator.make_token(user)
    frontend_base = getattr(settings, 'FRONTEND_PASSWORD_RESET_URL', None)
    if frontend_base:
        reset_url = f"{frontend_base}?uid={uid}&token={token}"
    else:
        reset_url = f"uid={uid}&token={token}"
    return uid, token, reset_url


def send_password_reset_email(user):
    """
    Send password reset email using UUID and token
    """
    uid, token, reset_url = make_password_reset_email(user)
    subject = "Password reset request"
    message = (
        f"Hello {user.email},\n\n"
        "You (or someone else) requested a password reset. "
        "If you did, click the link below to reset your password:\n\n"
        f"{reset_url}\n\n"
        "If you didn't request this, you can safely ignore this email.\n\n"
        "Regards,\nYour Team"
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
