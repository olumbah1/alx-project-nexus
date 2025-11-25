from django.conf import settings
from django.template.loader import render_to_string
from .models import Notification


def create_notification(recipient, verb, actor_user=None, target=None, description="", link="", email=False):
    # If recipient has disabled notifications, stop here
    try:
        if getattr(recipient, "notification_enabled", True) is False:
            return None
    except Exception:
        pass

    # --- Prepare target metadata safely ---
    target_type = ""
    target_id = ""

    if target is not None:
        try:
            target_type = target.__class__.__name__
            target_id = str(getattr(target, "pk", ""))
        except Exception:
            # If any issue, just leave both empty
            pass

    # --- Create the notification object ---
    notif = Notification.objects.create(
        recipient=recipient,
        actor_user=actor_user,
        verb=verb,
        target_type=target_type,
        target_id=target_id,
        description=description or "",
        link=link or "",
    )

    # --- If email enabled & user allows notifications, schedule email task ---
    if email and getattr(recipient, "notification_enabled", True):
        try:
            from .tasks import send_notification_email_task
            send_notification_email_task.delay(str(notif.pk), recipient.email)
        except Exception:
            pass

    return notif
