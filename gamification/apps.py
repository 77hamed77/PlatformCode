# gamification/apps.py

from django.apps import AppConfig

class GamificationConfig(AppConfig):
    """
    Configuration class for the 'gamification' app.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gamification'
    verbose_name = "التحفيز والإنجازات"

    def ready(self):
        # إذا قررت نقل الإشارات إلى هنا في المستقبل، فهذا هو المكان المناسب.
        # import gamification.signals
        pass