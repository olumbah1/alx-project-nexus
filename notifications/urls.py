# notifications/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.NotificationListView.as_view(), name="notifications-list"),
    path("unread-count/", views.UnreadCountView.as_view(), name="notifications-unread-count"),
    path("mark-read/", views.MarkAsReadView.as_view(), name="notifications-mark-read"),
    path("<uuid:pk>/mark-read/", views.MarkOneAsReadView.as_view(), name="notification-mark-one"),
    path("<uuid:pk>/", views.DeleteNotificationView.as_view(), name="notification-delete"),
]
