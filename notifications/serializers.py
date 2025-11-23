# notifications/serializers.py
from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    actor = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            "id", "recipient", "actor", "verb", "description", "link",
            "target_type", "target_id", "read", "emailed", "created_at"
        ]
        read_only_fields = ["id", "recipient", "actor", "emailed", "created_at"]

    def get_actor(self, obj):
        if obj.actor_user:
            # representation for actor
            return {"id": str(obj.actor_user.pk), "email": getattr(obj.actor_user, "email", None)}
        return None
