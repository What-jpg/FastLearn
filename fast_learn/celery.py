import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fast_learn.settings")

app = Celery('fast_learn')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()