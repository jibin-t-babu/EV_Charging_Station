from django.apps import AppConfig


class EvAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ev_app'
    def ready(self):
      import ev_app.signals


