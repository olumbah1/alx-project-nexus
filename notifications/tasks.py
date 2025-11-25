from celery import shared_task
from django.core.mail import send_mail
from .models import Notification

@shared_task(name="notifications.send_notification_email")
def send_notification_email_task(notification_id, recipient_email):
    try:
        notif = Notification.objects.get(pk=notification_id)
    except Notification.DoesNotExist:
        return

    # double-check user preference before sending
    recipient = notif.recipient
    if not getattr(recipient, "notification_enabled", True):
        return

    # render and send email (simplified)
    subject = f"New notification: {notif.verb}"
    message = notif.description or notif.verb
    send_mail(subject, message, "no-reply@example.com", [recipient_email])

    notif.emailed = True
    notif.save(update_fields=["emailed"])

    # If successful: notif.emailed = True; notif.save(update_fields=["emailed"])
