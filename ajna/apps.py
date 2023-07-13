from django.apps import AppConfig


class AjnaConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ajna"

    def ready(self):
        import ajna.signals  # noqa
