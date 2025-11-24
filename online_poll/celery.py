# online_poll/celery.py
import os
from celery import Celery

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'online_poll.settings')

# Create Celery app
app = Celery('online_poll')

# Load configuration from Django settings with CELERY namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Override broker URL to ensure it's set correctly
app.conf.broker_url = 'amqp://guest:guest@localhost:5672//'
app.conf.result_backend = 'rpc://'

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')