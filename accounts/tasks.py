from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator, default_token_generator
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

User = get_user_model()
token_generator = PasswordResetTokenGenerator()


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3, 'countdown': 5},
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True
)
def send_verification_email_task(self, user_id):
    """
    Asynchronous task to send email verification link.
    
    Args:
        user_id: UUID of the user (converted to string)
    """
    try:
        # Get user by UUID
        user = User.objects.get(id=user_id)
        
        # Generate token
        uid = str(user.id)
        token = default_token_generator.make_token(user)
        
        # Build verification URL
        verify_url = f"http://localhost:8000/api/auth/verify/{uid}/{token}/"
        
        # Prepare email
        subject = "Verify your email"
        message = (
            f"Hello {user.first_name},\n\n"
            f"Thank you for signing up! Please verify your email by clicking the link below:\n\n"
            f"{verify_url}\n\n"
            f"If you didn't create an account, please ignore this email.\n\n"
            f"Regards,\nYour Team"
        )
        
        # Send email
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        
        logger.info(f"Verification email sent successfully to {user.email}")
        return f"Email sent to {user.email}"
        
    except User.DoesNotExist:
        logger.error(f"User with id {user_id} does not exist")
        raise
    except Exception as e:
        logger.error(f"Failed to send verification email to user {user_id}: {str(e)}")
        raise self.retry(exc=e)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3, 'countdown': 5},
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True
)
def send_password_reset_email_task(self, user_id):
    """
    Asynchronous task to send password reset email.
    
    Args:
        user_id: UUID of the user (converted to string)
    """
    try:
        # Get user by UUID
        user = User.objects.get(id=user_id)
        
        # Generate token
        uid = str(user.id)
        token = token_generator.make_token(user)
        
        # Build reset URL
        frontend_base = getattr(settings, 'FRONTEND_PASSWORD_RESET_URL', None)
        if frontend_base:
            reset_url = f"{frontend_base}?uid={uid}&token={token}"
        else:
            reset_url = f"http://localhost:8000/reset-password?uid={uid}&token={token}"
        
        # Prepare email
        subject = "Password reset request"
        message = (
            f"Hello {user.first_name},\n\n"
            "You (or someone else) requested a password reset. "
            "If you did, click the link below to reset your password:\n\n"
            f"{reset_url}\n\n"
            "This link will expire in 24 hours.\n\n"
            "If you didn't request this, you can safely ignore this email.\n\n"
            "Regards,\nYour Team"
        )
        
        # Send email
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        
        logger.info(f"Password reset email sent successfully to {user.email}")
        return f"Password reset email sent to {user.email}"
        
    except User.DoesNotExist:
        logger.error(f"User with id {user_id} does not exist")
        raise
    except Exception as e:
        logger.error(f"Failed to send password reset email to user {user_id}: {str(e)}")
        raise self.retry(exc=e)