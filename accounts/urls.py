# accounts/urls.py

from django.urls import path
# 1. FIX: Import the Class-Based Views we created, not the old functions.
from .views import SignUpView, LeaderboardView

app_name = 'accounts' # BEST PRACTICE: Add an app namespace for clarity

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    
    # 2. FIX: Use the Class-Based View with .as_view()
    path('leaderboard/', LeaderboardView.as_view(), name='leaderboard'),
]