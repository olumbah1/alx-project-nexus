import os
from celery import Celery

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'online_poll.settings')

# Create Celery app
app = Celery('online_poll')

# Load configuration from Django settings with CELERY namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Use environment variables for broker and result backend
broker_url = os.getenv('CELERY_BROKER_URL')
result_backend = os.getenv('CELERY_RESULT_BACKEND')

if broker_url:
    app.conf.broker_url = broker_url
if result_backend:
    app.conf.result_backend = result_backend

# RabbitMQ specific settings
app.conf.broker_connection_retry_on_startup = True
app.conf.broker_connection_retry = True

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')