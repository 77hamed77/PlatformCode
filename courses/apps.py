# courses/apps.py
from django.apps import AppConfig

class CoursesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'courses'

    def ready(self):
        # هذا هو المكان الوحيد الذي يجب أن يتم فيه استيراد الإشارات
        import courses.signals