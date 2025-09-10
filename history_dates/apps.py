from django.apps import AppConfig


class HistoryDatesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'history_dates'

    def ready(self):
        from . import signals