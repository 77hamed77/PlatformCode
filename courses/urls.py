# courses/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.path_list_view, name='path_list'),
    path('<int:path_id>/', views.path_detail_view, name='path_detail'),
    path('course/<int:course_id>/', views.course_detail_view, name='course_detail'),
    
    # الرابط الجديد لوظيفة إكمال الدرس
    path('lesson/<int:lesson_id>/complete/', views.mark_lesson_complete, name='mark_lesson_complete'),
    path('quiz/<int:quiz_id>/', views.take_quiz_view, name='take_quiz'),
    path('quiz/result/<int:submission_id>/', views.quiz_result_view, name='quiz_result'),
]