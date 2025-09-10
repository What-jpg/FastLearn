from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

# Create your models here.
class HistoryDate(models.Model):
    class Meta:
        indexes = [
        ]

    date = models.CharField()
    events = models.TextField()


class TotalHistoryDates(models.Model):
    total_dates = models.IntegerField(default=0)