# problems/apps.py
from django.apps import AppConfig

class ProblemsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'problems'
    
    # تأكد من أن دالة ready فارغة أو محذوفة
    def ready(self):
        pass