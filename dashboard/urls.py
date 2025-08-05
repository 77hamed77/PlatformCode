# dashboard/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # الصفحة الرئيسية للوحة التحكم
    path('', views.dashboard_view, name='dashboard'),
    # روابط لإدارة المهام
    path('task/toggle/<int:task_id>/', views.toggle_task_status, name='toggle_task'),
    path('task/delete/<int:task_id>/', views.delete_task, name='delete_task'),
    path('note/new/', views.create_note_view, name='create_note'),
    path('note/edit/<int:note_id>/', views.edit_note_view, name='edit_note'),
    path('note/delete/<int:note_id>/', views.delete_note_view, name='delete_note'),
]