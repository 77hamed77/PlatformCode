# accounts/urls.py
from django.urls import path
from .views import SignUpView, leaderboard_view # أضف leaderboard_view

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('leaderboard/', leaderboard_view, name='leaderboard'), # <-- الرابط الجديد
]