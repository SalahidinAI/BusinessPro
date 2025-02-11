from django.apps import AppConfig


class RichmanConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'richman'

    def ready(self):
        import richman.signals
