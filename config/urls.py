# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView # لاستخدامه في الصفحة الرئيسية

urlpatterns = [
    path('admin/', admin.site.urls),

    # روابط المصادقة المدمجة (login, logout, password_reset, etc.)
    path('accounts/', include('django.contrib.auth.urls')),
    # روابط تطبيقنا المخصصة (signup)
    path('accounts/', include('accounts.urls')),

    # روابط تطبيق الكورسات
    path('paths/', include('courses.urls')),

    path('problems/', include('problems.urls')),
    
    path('dashboard/', include('dashboard.urls')),
    
    # إنشاء صفحة رئيسية مؤقتة للمشروع
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
]