# problems/views.py

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Exists, OuterRef
from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView, ListView, View

from .models import Problem, Submission
from .services import JudgingService


class ProblemListView(ListView):
    model = Problem
    template_name = 'problems/problem_list.html'
    context_object_name = 'problems'

    def get_queryset(self):
        """
        2. CRITICAL FIX (Performance): Uses annotation and a subquery to determine
           if a problem is solved, all within a single, efficient database query.
        """
        queryset = super().get_queryset()
        
        if self.request.user.is_authenticated:
            # Create a subquery that checks for the existence of a correct submission
            # for the "outer" problem's pk.
            solved_subquery = Submission.objects.filter(
                problem=OuterRef('pk'),
                student=self.request.user,
                status=Submission.Status.CORRECT
            )
            queryset = queryset.annotate(
                is_solved_by_user=Exists(solved_subquery)
            )
            
        return queryset


class ProblemDetailView(LoginRequiredMixin, DetailView):
    model = Problem
    template_name = 'problems/problem_detail.html'
    context_object_name = 'problem'
    pk_url_kwarg = 'pk' # Standardizing to pk

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.prefetch_related('test_cases')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 3. FIX (DRY): This logic is now encapsulated here.
        context['submissions'] = self.get_user_submissions()
        return context
    
    def get_user_submissions(self):
        """Helper method to fetch user submissions for this problem."""
        return Submission.objects.filter(
            problem=self.object,
            student=self.request.user
        ).order_by('-submitted_at')


class SubmissionCreateView(LoginRequiredMixin, View):
    """
    Handles POST requests for creating submissions.
    Uses HTMX for a seamless, partial-page update.
    """
    def post(self, request, *args, **kwargs):
        # The `prefetch_related` here ensures the JudgingService is efficient.
        problem = get_object_or_404(Problem.objects.prefetch_related('test_cases'), pk=kwargs['pk'])
        code = request.POST.get('code', '')

        # Delegate all judging logic to the service layer
        JudgingService.judge_submission(problem=problem, student=request.user, code=code)
        
        # 4. FIX (DRY): Instead of re-querying, we create an instance of the
        # DetailView to reuse its submission-fetching logic.
        detail_view = ProblemDetailView()
        detail_view.request = request
        detail_view.object = problem
        
        context = detail_view.get_context_data()
        
        return render(request, 'problems/partials/submission_history.html', context)