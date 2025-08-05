# accounts/views.py

# 1. Imports are grouped and organized at the top
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, Window
from django.db.models.functions import Rank
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from .forms import CustomUserCreationForm
from .models import CustomUser


# 2. Using a Class-Based View for SignUp, which is already good practice.
class SignUpView(CreateView):
    """
    Handles new user registration.
    Uses a generic CreateView for clean and maintainable code.
    """
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'accounts/signup.html'


# 3. Refactoring leaderboard_view into a more powerful Class-Based View
class LeaderboardView(TemplateView):
    """
    Displays the leaderboard with top students and the current user's rank.
    - Uses TemplateView for structured context management.
    - Optimized database queries for performance.
    """
    template_name = 'accounts/leaderboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # The query is executed only ONCE here.
        students_with_rank = CustomUser.objects.annotate(
            rank=Window(
                expression=Rank(),
                order_by=F('score').desc()
            )
        ).order_by('rank')

        # Convert the QuerySet to a list to avoid further database hits.
        ranked_list = list(students_with_rank[:20]) # We only care about the top 20

        # Separate the top 3 and the rest using Python slicing (much faster).
        top_three = ranked_list[:3]
        rest_of_students = ranked_list[3:]

        current_user_rank = None
        # Check for the current user's rank efficiently
        if self.request.user.is_authenticated:
            # 4. CRITICAL FIX: Find the user in the already-fetched list.
            # This avoids a second database query.
            for student in ranked_list:
                if student.id == self.request.user.id:
                    current_user_rank = student
                    break # Stop searching once found
            
            # Fallback: If the user is not in the top 20, get their rank with a specific query.
            if not current_user_rank:
                user_rank_obj = students_with_rank.filter(id=self.request.user.id).first()
                if user_rank_obj:
                    current_user_rank = user_rank_obj

        context.update({
            'top_three': top_three,
            'rest_of_students': rest_of_students,
            'current_user_rank': current_user_rank,
        })
        
        return context