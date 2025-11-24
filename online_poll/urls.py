from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from accounts.tasks import send_verification_email_task, send_password_reset_email_task
from django.contrib.auth import get_user_model

def test_celery_endpoint(request):
    """Quick test endpoint for Celery"""
    User = get_user_model()
    user = User.objects.first()
    
    if not user:
        return JsonResponse({'error': 'No users found in database'}, status=404)
    
    # Trigger both email tasks
    task1 = send_verification_email_task.delay(str(user.id))
    task2 = send_password_reset_email_task.delay(str(user.id))
    
    return JsonResponse({
        'status': 'success',
        'message': f'Email tasks triggered for {user.email}',
        'user_email': user.email,
        'user_id': str(user.id),
        'verification_task_id': str(task1.id),
        'reset_task_id': str(task2.id),
        'note': 'Check your Celery worker terminal to see task execution!'
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/test-celery/', test_celery_endpoint, name='test_celery'),
    path('api/', include('accounts.urls')),
    path('api/poll/', include('voteapp.urls')),
    path('api/notification/', include('notifications.urls'))
]