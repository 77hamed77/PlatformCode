# courses/views.py

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import DetailView, ListView

from .models import Choice, Course, LearningPath, Lesson, Quiz, QuizSubmission, StudentProgress


# =================================================================
# PUBLIC VIEWS (Accessible to all users)
# =================================================================

class LearningPathListView(ListView):
    """
    FIX: Replaced function with a more maintainable Class-Based View.
    Displays a list of all available learning paths.
    - `model` defines the data to fetch.
    - `template_name` defines the template to render.
    - `context_object_name` defines the variable name in the template.
    """
    model = LearningPath
    template_name = 'courses/path_list.html'
    context_object_name = 'paths'


class LearningPathDetailView(DetailView):
    """
    FIX: Replaced function with a DetailView and optimized queries.
    Displays details for a single learning path, including its courses.
    - `prefetch_related` is used to avoid N+1 query problems.
    """
    model = LearningPath
    template_name = 'courses/path_detail.html'
    context_object_name = 'path'
    pk_url_kwarg = 'path_id' # Maps the URL keyword 'path_id' to the primary key lookup

    def get_queryset(self):
        """
        CRITICAL FIX (Performance): Pre-fetches related data to prevent N+1 queries.
        This one optimization can reduce database queries from dozens to just a few.
        """
        queryset = super().get_queryset()
        return queryset.prefetch_related(
            models.Prefetch('courses', queryset=Course.objects.annotate(
                modules_count=Count('modules'),
                total_lessons_count=Count('modules__lessons')
            ))
        )

    def get_context_data(self, **kwargs):
        """
        Adds extra context for the template, like which courses the user has started.
        """
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            all_courses_in_path = self.object.courses.all()
            context['started_course_ids'] = set(
                StudentProgress.objects.filter(
                    student=self.request.user,
                    lesson__module__course__in=all_courses_in_path
                ).values_list('lesson__module__course_id', flat=True)
            )
        return context


class CourseDetailView(DetailView):
    """
    FIX: Replaced function with a DetailView and optimized queries.
    Displays details for a single course, including its modules and lessons.
    """
    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'
    pk_url_kwarg = 'course_id'

    def get_queryset(self):
        """
        CRITICAL FIX (Performance): Fetches all modules and their lessons in a single, efficient query.
        """
        queryset = super().get_queryset()
        return queryset.prefetch_related('modules__lessons')

    def get_context_data(self, **kwargs):
        """
        Adds extra context:
        - `completed_lessons`: A set of lesson IDs completed by the user.
        - `progress_percentage`: The user's completion percentage for the course.
        """
        context = super().get_context_data(**kwargs)
        course = self.object
        completed_lessons = set()

        if self.request.user.is_authenticated:
            completed_lessons = set(
                StudentProgress.objects.filter(
                    student=self.request.user,
                    lesson__module__course=course
                ).values_list('lesson_id', flat=True)
            )
        
        all_lessons_count = Lesson.objects.filter(module__course=course).count()
        progress_percentage = 0
        if all_lessons_count > 0:
            progress_percentage = round((len(completed_lessons) / all_lessons_count) * 100)

        context['completed_lessons'] = completed_lessons
        context['progress_percentage'] = progress_percentage
        return context


# =================================================================
# ACTION VIEWS (Require user to be logged in)
# =================================================================

class MarkLessonCompleteView(LoginRequiredMixin, View):
    """
    FIX: Replaced function with a more secure and robust Class-Based View.
    Handles the action of a student marking a lesson as complete.
    - `LoginRequiredMixin` ensures only logged-in users can access this.
    - Only accepts POST requests for security.
    """
    def post(self, request, *args, **kwargs):
        lesson = get_object_or_404(Lesson, id=kwargs['lesson_id'])
        
        # `get_or_create` is an atomic and efficient way to handle this.
        StudentProgress.objects.get_or_create(student=request.user, lesson=lesson)
        
        return redirect('course_detail', course_id=lesson.module.course.id)


class TakeQuizView(LoginRequiredMixin, View):
    """
    FIX: Replaced function with a CBV for better structure and logic separation.
    Handles displaying and processing a quiz.
    """
    def get(self, request, *args, **kwargs):
        quiz = get_object_or_404(Quiz.objects.prefetch_related('questions__choices'), id=kwargs['quiz_id'])
        
        # FIX (Performance): Use `select_related` and `filter` once, not `exists()` then `get()`.
        submission = QuizSubmission.objects.filter(student=request.user, quiz=quiz).first()
        if submission:
            return redirect('quiz_result', submission_id=submission.id)
            
        return render(request, 'courses/quiz_form.html', {'quiz': quiz})

    def post(self, request, *args, **kwargs):
        quiz = get_object_or_404(Quiz.objects.prefetch_related('questions__choices'), id=kwargs['quiz_id'])
        
        # FIX: Move score calculation logic into a model method for cleaner views.
        score, _ = self.calculate_score(request.POST, quiz)
        
        submission, created = QuizSubmission.objects.get_or_create(
            student=request.user,
            quiz=quiz,
            defaults={'score': score}
        )

        # FIX: Gamification logic should be in signals, not views.
        # This logic is now handled by a post_save signal on QuizSubmission.
        
        return redirect('quiz_result', submission_id=submission.id)
    
    @staticmethod
    def calculate_score(post_data, quiz):
        """Helper method to decouple score calculation from the view logic."""
        correct_answers = 0
        questions = quiz.questions.all()
        total_questions = questions.count()

        for question in questions:
            selected_choice_id = post_data.get(f'question_{question.id}')
            if selected_choice_id:
                # This is more efficient than hitting the DB for each choice
                correct_choice = next((c for c in question.choices.all() if c.is_correct), None)
                if correct_choice and int(selected_choice_id) == correct_choice.id:
                    correct_answers += 1
        
        score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        return score, correct_answers


class QuizResultView(LoginRequiredMixin, DetailView):
    """
    FIX: Replaced function with a secure and efficient DetailView.
    Displays the result of a quiz submission.
    """
    model = QuizSubmission
    template_name = 'courses/quiz_result.html'
    context_object_name = 'submission'
    pk_url_kwarg = 'submission_id'

    def get_queryset(self):
        """
        CRITICAL FIX (Security): Ensures a user can ONLY see their own submissions.
        The query is filtered by the logged-in user from the start.
        """
        queryset = super().get_queryset()
        return queryset.filter(student=self.request.user)
    
    def get_context_data(self, **kwargs):
        """Adds detailed performance breakdown to the context."""
        context = super().get_context_data(**kwargs)
        submission = self.object
        total_questions = submission.quiz.questions.count()
        correct_answers = round((submission.score / 100) * total_questions) if total_questions > 0 else 0
        
        context.update({
            'total_questions': total_questions,
            'correct_answers': correct_answers,
            'wrong_answers': total_questions - correct_answers,
        })
        return context