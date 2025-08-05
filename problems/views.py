# problems/views.py

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import DetailView, ListView, View

from .models import Problem, Submission
from .services import JudgingService


class ProblemListView(ListView):
    """
    يعرض قائمة بجميع المسائل المتاحة.
    """
    model = Problem
    template_name = 'problems/problem_list.html'
    context_object_name = 'problems'

    def get_context_data(self, **kwargs):
        """
        يضيف سمة محسوبة لكل مسألة لتحديد ما إذا كان المستخدم قد حلها.
        """
        context = super().get_context_data(**kwargs)
        user = self.request.user
        solved_ids = set()
        
        if user.is_authenticated:
            solved_ids = set(
                Submission.objects.filter(student=user, status=Submission.Status.CORRECT)
                                  .values_list('problem_id', flat=True)
            )
        
        problem_list = context['problems']
        for problem in problem_list:
            problem.is_solved_by_user = problem.id in solved_ids
            
        context['problems'] = problem_list
        return context


class ProblemDetailView(LoginRequiredMixin, DetailView):
    """
    يعرض تفاصيل مسألة واحدة وسجل تقديمات المستخدم لها.
    """
    model = Problem
    template_name = 'problems/problem_detail.html'
    context_object_name = 'problem'
    pk_url_kwarg = 'problem_id'

    def get_queryset(self):
        """
        يحسن الأداء عبر جلب كل حالات الاختبار المتعلقة في استعلام واحد.
        """
        queryset = super().get_queryset()
        return queryset.prefetch_related('test_cases')

    def get_context_data(self, **kwargs):
        """
        يضيف سجل تقديمات المستخدم لهذه المسألة.
        """
        context = super().get_context_data(**kwargs)
        context['submissions'] = Submission.objects.filter(
            problem=self.object,
            student=self.request.user
        ).order_by('-submitted_at')
        return context


class SubmissionCreateView(LoginRequiredMixin, View):
    """
    يعالج طلبات إنشاء التقديمات (POST فقط) ويستخدم HTMX لتجربة سلسة.
    """
    def post(self, request, *args, **kwargs):
        problem = get_object_or_404(Problem.objects.prefetch_related('test_cases'), pk=kwargs['problem_id'])
        code = request.POST.get('code', '')

        # يفوض كل منطق الحكم إلى طبقة الخدمات
        JudgingService.judge_submission(problem=problem, student=request.user, code=code)
        
        # يرجع القالب الجزئي المحدث لسجل التقديمات لـ HTMX
        submissions = Submission.objects.filter(problem=problem, student=request.user).order_by('-submitted_at')
        return render(request, 'problems/partials/submission_history.html', {'submissions': submissions})