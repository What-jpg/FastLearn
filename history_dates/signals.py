from django.dispatch import receiver
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from .models import HistoryDate, TotalHistoryDates
from .utils import TotalHistoryDatesRedisKeys

@receiver(post_save, sender=HistoryDate)
def history_date_created(sender, instance, created, **kwargs):
    if created:
        tot_history_dates_instance = TotalHistoryDates.objects.first()

        if tot_history_dates_instance :
            tot_history_dates_instance.total_dates += 1
            tot_history_dates_instance.save()

            redis_key = TotalHistoryDatesRedisKeys.get()

            if cache.get(redis_key):
                cache.set(redis_key, tot_history_dates_instance.total_dates, 60)
        else:
            TotalHistoryDates.objects.create(total_dates=1)

@receiver(post_delete, sender=HistoryDate)
def history_date_created(sender, instance, **kwargs):
    tot_history_dates_instance = TotalHistoryDates.objects.first()

    tot_history_dates_instance.total_dates -= 1
    tot_history_dates_instance.save()

    redis_key = TotalHistoryDatesRedisKeys.get()

    if cache.get(redis_key):
        cache.set(redis_key, tot_history_dates_instance.total_dates, 60)