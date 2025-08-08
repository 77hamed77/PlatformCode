# ai_tutor/urls.py
from django.urls import path
from .views import AskAITutorView

app_name = 'ai_tutor'

urlpatterns = [
    path('ask/', AskAITutorView.as_view(), name='ask'),
]