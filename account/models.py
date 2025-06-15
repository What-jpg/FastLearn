from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.auth import get_user_model
from .managers import SocialManager, LocalManager

class User(AbstractUser):
    is_two_factor_auth_active = models.BooleanField(default=False)

    objects = UserManager()
    social = SocialManager()
    local = LocalManager()

    def __str__(self):
        return self.email
    
# Create your models here.
class Subscribtion(models.Model):
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE
    )
    subscription_type = models.TextField(max_length=10, default="Free")
    subscription_started = models.DateField(auto_now_add=True)