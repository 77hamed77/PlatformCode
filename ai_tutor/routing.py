# ai_tutor/routing.py

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/ai_tutor/$', consumers.TutorConsumer.as_asgi()),
]