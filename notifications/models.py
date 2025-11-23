from django.db import models
# notifications/models.py
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Notification(models.Model):
    """
    Stores one notification delivered to a single user.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    actor_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="actions")
    verb = models.CharField(max_length=200)  # e.g. "created a poll", "voted on"
    target_type = models.CharField(max_length=50, blank=True)  # optional: "Poll", "Comment"
    target_id = models.CharField(max_length=100, blank=True)   # optional: pk of target (string to support UUID)
    description = models.TextField(blank=True)  # optional longer text
    link = models.CharField(max_length=500, blank=True)  # frontend URL to navigate to
    read = models.BooleanField(default=False)
    emailed = models.BooleanField(default=False)  # was an email sent for this notification
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "read"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return f"Notif to {self.recipient}: {self.verb}"

