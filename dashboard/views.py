# dashboard/views.py

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch, Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from courses.models import Course, StudentProgress, Lesson
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
        """Uses the custom manager for clean, reusable queries."""
        return Task.objects.for_user(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context['task_form'] = TaskForm()
        context['notes'] = Note.objects.filter(student=user)[:5]

        # Pre-calculate all stats efficiently
        stats = {
            'solved_problems': user.get_solved_problems_count(),
            'completed_lessons': user.progress_records.count(),
            'rank': None, # Rank calculation can be complex, add later if needed
        }
        context['stats'] = stats

        # Fetch in-progress courses and their progress percentage
        in_progress_courses_qs = Course.objects.filter(
            lessons__progress_records__student=user
        ).distinct().select_related('instructor').annotate(
            total_lessons_count=Count('lessons', distinct=True)
        )[:3]

        in_progress_courses_with_progress = []
        for course in in_progress_courses_qs:
            completed = StudentProgress.objects.filter(student=user, lesson__course=course).count()
            percentage = round((completed / course.total_lessons_count) * 100) if course.total_lessons_count > 0 else 0
            in_progress_courses_with_progress.append({'course': course, 'percentage': percentage})
        
        context['in_progress_courses_with_progress'] = in_progress_courses_with_progress
        
        # Fetch last solved problems efficiently
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

    def form_valid(self, form):
        form.instance.student = self.request.user
        self.object = form.save()
        # For HTMX, return the partial template with just the new task
        return render(self.request, 'dashboard/partials/task_list.html', {'tasks': [self.object]})

    def form_invalid(self, form):
        # Handle invalid form submission if needed, e.g., return an error message
        return HttpResponse('العنوان مطلوب.', status=400)


class TaskToggleView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        task = get_object_or_404(Task, pk=kwargs['pk'], student=request.user)
        task.toggle()
        # Return the updated task partial for HTMX to swap
        return render(request, 'dashboard/partials/task_list.html', {'tasks': [task]})


class TaskDeleteView(LoginRequiredMixin, View):
    def delete(self, request, *args, **kwargs):
        task = get_object_or_404(Task, pk=kwargs['pk'], student=request.user)
        task.delete()
        # Return an empty response with status 200, HTMX will remove the element
        return HttpResponse('')

# =================================================================
# Standard Note Views (Full page reload)
# =================================================================

class NoteCreateView(LoginRequiredMixin, CreateView):
    model = Note
    form_class = NoteForm
    template_name = 'dashboard/note_form.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        form.instance.student = self.request.user
        return super().form_valid(form)


class NoteUpdateView(LoginRequiredMixin, UpdateView):
    model = Note
    form_class = NoteForm
    template_name = 'dashboard/note_form.html'
    success_url = reverse_lazy('dashboard')

    def get_queryset(self):
        return Note.objects.filter(student=self.request.user)


class NoteDeleteView(LoginRequiredMixin, DeleteView):
    model = Note
    success_url = reverse_lazy('dashboard')
    template_name = 'dashboard/note_confirm_delete.html'

    def get_queryset(self):
        return Note.objects.filter(student=self.request.user)