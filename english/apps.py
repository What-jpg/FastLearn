from django.apps import AppConfig


class EnglishConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'english'

    def ready(self):
        from . import signals