from django.db import models

class SocialManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().exclude(social_auth=None).all()
    
class LocalManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(social_auth=None).all()