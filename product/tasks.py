from celery import shared_task
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from datetime import timedelta
from django.utils import timezone

User = get_user_model()


@shared_task
def send_welcome_email():
    one_day_ago = timezone.now() - timedelta(days=1)
    new_users = User.objects.filter(date_joined__gt=one_day_ago)

    for user in new_users:
        send_mail(
            'Welcome to our Skyloov website',
            f'Hi {user.username}, thank you for registering on our website. We hope you enjoy our platform!',
            'www.skyloov.com',
            [user.email],
            fail_silently=False,
        )
