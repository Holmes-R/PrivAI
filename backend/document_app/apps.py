from django.apps import AppConfig


class DocumentAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'document_app'

    def ready(self):
        import document_app.signals