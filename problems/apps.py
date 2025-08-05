# problems/apps.py
from django.apps import AppConfig

class ProblemsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'problems'

    # The ready() method that imported signals should be REMOVED from here.