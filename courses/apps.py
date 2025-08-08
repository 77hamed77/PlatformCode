# courses/apps.py

from django.apps import AppConfig

class CoursesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'courses'

    def ready(self):
        # هذا السطر هو الذي يقوم بتسجيل جميع الإشارات الموجودة في ملف signals.py
        # إذا كان هذا السطر مفقودًا، فلن تعمل الإشارات أبدًا.
        import courses.signals