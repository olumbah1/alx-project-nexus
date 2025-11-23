from django.conf import settings
from django.template.loader import render_to_string
from .models import Notification

def create_notification(recipient, verb, actor_user=None, target=None, description="", link="", email=False):
    target_type = ""
    target_id = ""
    if target is not None:
        try:
            target_type = target.__class__.__name__
            target_id = str(getattr(target, "pk", ""))
        except Exception:
            pass

    notif = Notification.objects.create(
        recipient=recipient,
        actor_user=actor_user,
        verb=verb,
        target_type=target_type,
        target_id=target_id,
        description=description or "",
        link=link or "",
    )

    if email:
        # schedule Celery task (non-blocking)
        try:
            from .tasks import send_notification_email_task
            # pass notification id and recipient email; the task will render template and send
            send_notification_email_task.delay(str(notif.pk), recipient.email)
        except Exception:
            # fallback: do nothing or log — do not raise in signal
            pass

    return notif
