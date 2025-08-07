# dashboard/views.py

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from courses.models import Course, StudentProgress
from problems.models import Submission
from .forms import NoteForm, TaskForm
from .models import Note, Task

# =================================================================
# Main Dashboard View
# =================================================================

class DashboardView(LoginRequiredMixin, ListView):
    template_name = 'dashboard/dashboard.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        return Task.objects.for_user(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context['task_form'] = TaskForm()
        context['notes'] = Note.objects.filter(student=user).order_by('-updated_at')[:5]

        stats = {
            'solved_problems': user.get_solved_problems_count(),
            'completed_lessons': user.progress_records.count(),
            'rank': None,
        }
        context['stats'] = stats
        
        in_progress_course_ids = StudentProgress.objects.filter(student=user).values_list('lesson__course_id', flat=True).distinct()
        in_progress_courses_qs = Course.objects.filter(pk__in=list(in_progress_course_ids)).select_related('instructor').annotate(total_lessons_count=Count('lessons', distinct=True))[:3]

        in_progress_courses_with_progress = []
        for course in in_progress_courses_qs:
            completed_count = StudentProgress.objects.filter(student=user, lesson__course=course).count()
            total_count = course.total_lessons_count
            percentage = round((completed_count / total_count) * 100) if total_count > 0 else 0
            in_progress_courses_with_progress.append({'course': course, 'percentage': percentage})
        
        context['in_progress_courses_with_progress'] = in_progress_courses_with_progress
        
        context['last_solved_problems'] = Submission.objects.filter(student=user, status='Correct').select_related('problem').order_by('-submitted_at')[:3]
        
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
    # CRITICAL FIX: Changed from `delete` to `post` to match the HTMX form request.
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