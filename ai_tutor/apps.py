# ai_tutor/apps.py

from django.apps import AppConfig

class AiTutorConfig(AppConfig):
    """
    Configuration class for the 'ai_tutor' app.
    This defines the application for the Django project.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ai_tutor'
    verbose_name = "المساعد الذكي" # اسم وصفي سيظهر في لوحة التحكم