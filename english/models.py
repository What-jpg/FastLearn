from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

# Create your models here.
class EnglishWords(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['added']),
            models.Index(fields=['-added']),
            models.Index(fields=['streak']),
            models.Index(fields=['last_check'])
        ]

    word = models.CharField()
    translations = models.JSONField(default=list, null=True, blank=True)
    added = models.DateTimeField(default=timezone.now)
    streak = models.IntegerField(default=0)
    last_check = models.DateTimeField(blank=True)
    total_invokes = models.IntegerField(default=0)

    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE
    )

    def save(self, *args, **kwargs):
        if not self.last_check:
            self.last_check = self.added

        super().save(*args, **kwargs)


class TotalEnglishWords(models.Model):
    total_words = models.IntegerField(default=0)

    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE
    )