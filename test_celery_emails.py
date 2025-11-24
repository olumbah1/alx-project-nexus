# test_celery_emails.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'online_poll.settings')
django.setup()

# Import the Celery app FIRST to ensure it's configured
from online_poll.celery import app as celery_app

# Now import tasks
from accounts.tasks import send_verification_email_task, send_password_reset_email_task
from django.contrib.auth import get_user_model

User = get_user_model()

# Get a user
user = User.objects.first()

if user:
    print(f"Testing with user: {user.email} (ID: {user.id})")
    
    # Verify Celery is configured
    print(f"Celery Broker URL: {celery_app.conf.broker_url}")
    
    # Test verification email
    print("\n--- Sending Verification Email ---")
    task1 = send_verification_email_task.delay(str(user.id))
    print(f"Task ID: {task1.id}")
    print("✅ Task sent! Check your Celery worker terminal for execution!")
    
    # Test password reset email
    print("\n--- Sending Password Reset Email ---")
    task2 = send_password_reset_email_task.delay(str(user.id))
    print(f"Task ID: {task2.id}")
    print("✅ Task sent! Check your Celery worker terminal for execution!")
else:
    print("No users found. Creating a test user...")
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        first_name='Test'
    )
    print(f"Created user: {user.email}")
    
    # Test with new user
    task = send_verification_email_task.delay(str(user.id))
    print(f"Task ID: {task.id}")
    print("✅ Task sent! Check your Celery worker terminal!")