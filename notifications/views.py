# notifications/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Notification
from .serializers import NotificationSerializer
from django.db.models import Count

class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).order_by("-created_at")

class UnreadCountView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        count = Notification.objects.filter(recipient=request.user, read=False).count()
        return Response({"unread_count": count})

class MarkAsReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        ids = request.data.get("ids", None)
        if ids is None:
            return Response({"detail": "Provide 'ids' list."}, status=status.HTTP_400_BAD_REQUEST)
        qs = Notification.objects.filter(recipient=request.user, id__in=ids)
        updated = qs.update(read=True)
        return Response({"updated": updated})

class MarkOneAsReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, pk):
        try:
            notif = Notification.objects.get(pk=pk, recipient=request.user)
        except Notification.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        notif.read = True
        notif.save(update_fields=["read"])
        return Response({"detail": "Marked read"})

class DeleteNotificationView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def delete(self, request, pk):
        try:
            notif = Notification.objects.get(pk=pk, recipient=request.user)
        except Notification.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        notif.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

