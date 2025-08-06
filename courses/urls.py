# courses/urls.py

from django.urls import path
# 1. FIX: Import all the new Class-Based Views.
from .views import (
    LearningPathListView,
    LearningPathDetailView,
    CourseDetailView,
    MarkLessonCompleteView,
    TakeQuizView,
    QuizResultView,
)

app_name = 'courses' # BEST PRACTICE: Add an app namespace

urlpatterns = [
    # Path for listing all learning paths
    path('', LearningPathListView.as_view(), name='path_list'),

    # Path for a single learning path's details
    # 2. FIX: Use 'pk' as the standard keyword for primary keys.
    path('<int:pk>/', LearningPathDetailView.as_view(), name='path_detail'),

    # Path for a single course's details
    path('course/<int:pk>/', CourseDetailView.as_view(), name='course_detail'),
    
    # Path for the action of completing a lesson
    path('lesson/<int:pk>/complete/', MarkLessonCompleteView.as_view(), name='mark_lesson_complete'),

    # Paths for taking a quiz and seeing the result
    path('quiz/<int:pk>/', TakeQuizView.as_view(), name='take_quiz'),
    path('quiz/result/<int:pk>/', QuizResultView.as_view(), name='quiz_result'),
]