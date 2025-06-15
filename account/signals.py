from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from .models import Subscribtion

@receiver(post_save, sender=get_user_model())
def user_created(sender, instance, created, **kwargs):
    if created:
        Subscribtion.objects.create(user=instance)
    