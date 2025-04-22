from celery import shared_task
from django.core.mail import send_mail
from datetime import datetime

@shared_task
def send_registration_email(email):
    subject = "Welcome to ProjectManager!"
    message = "Thanks for signing up. Let us know if you need help."
    from_email = "no-reply@yourapp.com"
    recipient_list = [email]
    
    send_mail(subject, message, from_email, recipient_list)

@shared_task
def print_every_minute():
    print(f"✅ Beat task ran at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    