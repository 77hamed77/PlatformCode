# chat/apps.py

from django.apps import AppConfig

class ChatConfig(AppConfig):
    """
    Configuration class for the 'chat' app.
    This is where the app is defined and where signals (if any)
    would be connected in the `ready` method.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chat'
    verbose_name = "المجتمع والنقاشات" # اسم وصفي سيظهر في لوحة التحكم