# chat/routing.py

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # نستخدم re_path للتعامل مع الروابط التي تحتوي على متغيرات (مثل اسم الغرفة)
    re_path(r'ws/chat/(?P<room_slug>\w+)/$', consumers.ChatConsumer.as_asgi()),
]