from django.http import JsonResponse
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

def home(request):
    return JsonResponse({
        "message": "Welcome to the Student Guidance System API!",
        "status": "running"
    })

def cache_test_view(request):
    return JsonResponse({
        "cached_at": timezone.now().isoformat(),
        "message": "This response is cached for 15 minutes!"
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_email_view(request):
    to_email = request.data.get('to_email')
    if not to_email:
        return JsonResponse({
            'status': 'error',
            'message': 'Please provide "to_email" in the request body'
        }, status=400)
    
    try:
        send_mail(
            'Test Email from Student Guidance System',
            f'Hello! This is a test email sent to {to_email}',
            settings.DEFAULT_FROM_EMAIL,
            [to_email],
            fail_silently=False,
        )
        return JsonResponse({
            'status': 'success',
            'message': f'Email sent to {to_email}'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)