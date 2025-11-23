from django.apps import AppConfig

class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notifications'
    verbose_name = "Notifications"

    def ready(self):
        # import signal handlers
        import notifications.signals  # safe because signals use apps.get_model lazily
