# problems/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # صفحة قائمة كل المسائل
    path('', views.problem_list_view, name='problem_list'),
    # صفحة تفاصيل مسألة واحدة ومعالجة التقديم
    path('<int:problem_id>/', views.problem_detail_view, name='problem_detail'),
]