# config/urls.py

from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),

    # Local Apps
    path('accounts/', include('accounts.urls')),
    path('courses/', include('courses.urls')),
    path('problems/', include('problems.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('chat/', include('chat.urls')),
    path('ai-tutor/', include('ai_tutor.urls')),
    path('gamification/', include('gamification.urls')),
    
    # Django's built-in auth URLs (login, logout, password_reset, etc.)
    # It's better to place this under the 'accounts/' path for consistency
    path('accounts/', include('django.contrib.auth.urls')),

    # Home Page
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
]