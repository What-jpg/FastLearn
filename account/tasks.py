from celery import shared_task
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

@shared_task
def send_auth_code_email(uri_main, user_email, code, action):
    subject = "Email verification"
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = user_email
    html_content = render_to_string(
            "account/email_verification_email.html", 
            {'prot_host': uri_main, 'action': action, 'email': to_email, 'code': code}
        )
    
    mail = EmailMessage(
        subject=subject,
        body=html_content,
        from_email=from_email,
        to=[to_email]
    )
    mail.content_subtype = 'html'
    
    return mail.send(fail_silently=True)