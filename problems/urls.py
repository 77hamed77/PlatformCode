# problems/urls.py

from django.urls import path
# 1. FIX: Import all the new Class-Based Views.
from .views import (
    ProblemListView,
    ProblemDetailView,
    SubmissionCreateView,
)

app_name = 'problems' # BEST PRACTICE: Add an app namespace

urlpatterns = [
    # Path for listing all available problems
    path('', ProblemListView.as_view(), name='problem_list'),

    # Path for displaying a single problem's details (handles GET requests)
    # 2. FIX: Use 'pk' as the standard keyword for primary keys.
    path('problem/<int:pk>/', ProblemDetailView.as_view(), name='problem_detail'),

    # 3. CRITICAL FIX: Add a dedicated path for handling the code submission (handles POST requests)
    # This URL will be the target for the form in `problem_detail.html`.
    path('problem/<int:pk>/submit/', SubmissionCreateView.as_view(), name='problem_submit'),
]