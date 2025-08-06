# dashboard/urls.py

from django.urls import path
# 1. FIX: Import all the new Class-Based Views.
from .views import (
    DashboardView,
    TaskCreateView,
    TaskToggleView,
    TaskDeleteView,
    NoteCreateView,
    NoteUpdateView,
    NoteDeleteView,
)

app_name = 'dashboard' # BEST PRACTICE: Add an app namespace

urlpatterns = [
    # Main Dashboard
    path('', DashboardView.as_view(), name='dashboard'),

    # Task Management URLs (now using Class-Based Views)
    # Note: Task creation is handled by DashboardView, but we need a URL for the form action
    path('task/create/', TaskCreateView.as_view(), name='task_create'),
    path('task/toggle/<int:pk>/', TaskToggleView.as_view(), name='task_toggle'),
    path('task/delete/<int:pk>/', TaskDeleteView.as_view(), name='task_delete'),

    # Note Management URLs (now using Class-Based Views)
    path('note/new/', NoteCreateView.as_view(), name='note_create'),
    path('note/edit/<int:pk>/', NoteUpdateView.as_view(), name='note_update'),
    path('note/delete/<int:pk>/', NoteDeleteView.as_view(), name='note_delete'),
]