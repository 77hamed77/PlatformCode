# dashboard/views.py

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, OuterRef, Subquery
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

# Import models from all relevant apps
from courses.models import Course, StudentProgress
from problems.models import Submission
from ai_tutor.models import TutorConversation
from gamification.models import StudentBadge # <-- استيراد نموذج شارات الطالب
from .forms import NoteForm, TaskForm
from .models import Note, Task

# =================================================================
# Main Dashboard View
# =================================================================

class DashboardView(LoginRequiredMixin, ListView):
    template_name = 'dashboard/dashboard.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        """Uses the custom manager defined in the model for clean, reusable queries."""
        return Task.objects.for_user(self.request.user)

    def get_context_data(self, **kwargs):
        """
        Gathers all necessary context for the dashboard in the most efficient way possible.
        """
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # --- Base Context ---
        context['task_form'] = TaskForm()
        context['notes'] = Note.objects.filter(student=user).order_by('-updated_at')[:5]
        context['last_tutor_conversation'] = TutorConversation.objects.filter(student=user).prefetch_related('messages').first()

        # --- CRITICAL FIX: Fetch student badges and add them to the context ---
        context['student_badges'] = StudentBadge.objects.filter(student=user).select_related('badge').order_by('-awarded_at')

        # --- Pre-calculated Stats ---
        stats = {
            'solved_problems': user.get_solved_problems_count(),
            'completed_lessons': user.progress_records.count(),
            'rank': None, # Rank calculation is expensive; better to do it on a dedicated page
        }
        context['stats'] = stats
        
        # --- Efficiently Fetch in-progress courses and their progress ---
        completed_lessons_subquery = StudentProgress.objects.filter(
            student=user,
            lesson__course=OuterRef('pk')
        ).values('lesson__course').annotate(c=Count('pk')).values('c')

        in_progress_course_ids = StudentProgress.objects.filter(
            student=user
        ).values_list('lesson__course_id', flat=True).distinct()

        in_progress_courses_qs = Course.objects.filter(
            pk__in=list(in_progress_course_ids)
        ).select_related('instructor').annotate(
            total_lessons_count=Count('lessons', distinct=True),
            completed_lessons_count=Subquery(completed_lessons_subquery)
        )[:3]

        in_progress_courses_with_progress = []
        for course in in_progress_courses_qs:
            completed = course.completed_lessons_count or 0
            total = course.total_lessons_count
            percentage = round((completed / total) * 100) if total > 0 else 0
            in_progress_courses_with_progress.append({'course': course, 'percentage': percentage})
        
        context['in_progress_courses_with_progress'] = in_progress_courses_with_progress
        
        # --- Other Feeds ---
        context['last_solved_problems'] = Submission.objects.filter(
            student=user, status='Correct'
        ).select_related('problem').order_by('-submitted_at')[:3]
        
        return context

# =================================================================
# HTMX-powered Task Views
# =================================================================

class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    success_url = reverse_lazy('dashboard:dashboard')

    def form_valid(self, form):
        form.instance.student = self.request.user
        self.object = form.save()
        return render(self.request, 'dashboard/partials/task_list.html', {'tasks': [self.object]})

    def form_invalid(self, form):
        return HttpResponse('العنوان مطلوب.', status=400)

class TaskToggleView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        task = get_object_or_404(Task, pk=kwargs['pk'], student=request.user)
        task.toggle()
        return render(self.request, 'dashboard/partials/task_list.html', {'tasks': [task]})

class TaskDeleteView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        task = get_object_or_404(Task, pk=kwargs['pk'], student=request.user)
        task.delete()
        return HttpResponse('')

# =================================================================
# Standard Note Views (Full page reload)
# =================================================================

class NoteCreateView(LoginRequiredMixin, CreateView):
    model = Note
    form_class = NoteForm
    template_name = 'dashboard/note_form.html'
    success_url = reverse_lazy('dashboard:dashboard')

    def form_valid(self, form):
        form.instance.student = self.request.user
        return super().form_valid(form)

class NoteUpdateView(LoginRequiredMixin, UpdateView):
    model = Note
    form_class = NoteForm
    template_name = 'dashboard/note_form.html'
    success_url = reverse_lazy('dashboard:dashboard')

    def get_queryset(self):
        return Note.objects.filter(student=self.request.user)

class NoteDeleteView(LoginRequiredMixin, DeleteView):
    model = Note
    success_url = reverse_lazy('dashboard:dashboard')
    template_name = 'dashboard/note_confirm_delete.html'

    def get_queryset(self):
        return Note.objects.filter(student=self.request.user)