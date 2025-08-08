# accounts/views.py

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import F, Window
from django.db.models.functions import Rank
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView

from .forms import CustomUserCreationForm, ProfileUpdateForm
from .models import CustomUser


class SignUpView(CreateView):
    """Handles new user registration."""
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'accounts/signup.html'


class LeaderboardView(TemplateView):
    """Displays the leaderboard with top students and the current user's rank."""
    template_name = 'accounts/leaderboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        students_with_rank = CustomUser.objects.annotate(
            rank=Window(expression=Rank(), order_by=F('score').desc())
        ).order_by('rank')

        ranked_list = list(students_with_rank[:20])
        context['top_three'] = ranked_list[:3]
        context['rest_of_students'] = ranked_list[3:]

        current_user_rank = None
        if self.request.user.is_authenticated:
            # Find the user in the already-fetched list first
            for student in ranked_list:
                if student.id == self.request.user.id:
                    current_user_rank = student
                    break
            
            # If not in the top 20, fetch their specific rank
            if not current_user_rank:
                user_rank_obj = students_with_rank.filter(id=self.request.user.id).first()
                if user_rank_obj:
                    current_user_rank = user_rank_obj

        context['current_user_rank'] = current_user_rank
        return context


class ProfileUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    Allows authenticated users to update their own profile information.
    """
    model = CustomUser
    form_class = ProfileUpdateForm
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('accounts:profile')
    success_message = "تم تحديث ملفك الشخصي بنجاح!"

    def get_object(self, queryset=None):
        """Ensures the user can only edit their own profile."""
        return self.request.user