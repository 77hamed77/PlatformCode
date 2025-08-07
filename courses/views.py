# courses/views.py

# ----------------------------------------------------------------
# Imports (Cleaned and organized)
# ----------------------------------------------------------------
import math
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import DetailView, ListView

from .models import Choice, Course, LearningPath, Lesson, Quiz, QuizSubmission, StudentProgress

# =================================================================
# PUBLIC VIEWS (Accessible to all users)
# =================================================================

class LearningPathListView(ListView):
    """
    يعرض قائمة بجميع المسارات التعليمية المتاحة.
    - يستخدم ListView ليكون الكود موجزًا ومعياريًا.
    """
    model = LearningPath
    template_name = 'courses/path_list.html'
    context_object_name = 'paths'


class LearningPathDetailView(DetailView):
    """
    يعرض تفاصيل مسار تعليمي واحد، بما في ذلك كورساته.
    - مُحسَّن للأداء باستخدام prefetch_related و annotate.
    """
    model = LearningPath
    template_name = 'courses/path_detail.html'
    context_object_name = 'path'
    pk_url_kwarg = 'pk'  # موحد لاستخدام 'pk' من الـ URL

    def get_queryset(self):
        """
        تحسين الأداء الحرج: يجلب مسبقًا جميع البيانات ذات الصلة
        لمنع مشاكل N+1 query في القالب.
        """
        queryset = super().get_queryset()
        return queryset.prefetch_related(
            Prefetch('courses', queryset=Course.objects.annotate(
                # حساب عدد الوحدات والدروس على مستوى قاعدة البيانات
                modules_count=Count('modules', distinct=True),
                total_lessons_count=Count('lessons', distinct=True)
            ))
        )

    def get_context_data(self, **kwargs):
        """
        يضيف بيانات إضافية إلى السياق، مثل الكورسات التي بدأها المستخدم.
        """
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            all_courses_in_path = self.object.courses.all()
            context['started_course_ids'] = set(
                StudentProgress.objects.filter(
                    student=self.request.user,
                    lesson__course__in=all_courses_in_path
                ).values_list('lesson__course_id', flat=True)
            )
        return context


class CourseDetailView(DetailView):
    """
    يعرض تفاصيل كورس واحد، بما في ذلك وحداته ودروسه.
    - مُحسَّن للأداء ومصمم لحساب وعرض تقدم المستخدم.
    """
    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'
    pk_url_kwarg = 'pk'

    def get_queryset(self):
        """
        تحسين الأداء: يجلب الكورس مع عدد دروسه، وجميع وحداته ودروسها
        في استعلامات قليلة وفعالة.
        """
        queryset = super().get_queryset()
        queryset = queryset.annotate(total_lessons_count=Count('lessons', distinct=True))
        return queryset.prefetch_related('modules__lessons')

    def get_context_data(self, **kwargs):
        """
        يضيف بيانات التقدم: الدروس المكتملة والنسبة المئوية للإنجاز.
        """
        context = super().get_context_data(**kwargs)
        course = self.object
        completed_lessons = set()

        if self.request.user.is_authenticated:
            completed_lessons = set(
                StudentProgress.objects.filter(
                    student=self.request.user,
                    lesson__course=course
                ).values_list('lesson_id', flat=True)
            )
        
        all_lessons_count = course.total_lessons_count
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
    يعالج إجراء تعليم درس على أنه مكتمل (POST فقط للأمان).
    """
    def post(self, request, *args, **kwargs):
        lesson = get_object_or_404(Lesson, pk=kwargs['pk'])
        StudentProgress.objects.get_or_create(student=request.user, lesson=lesson)
        return redirect('courses:course_detail', pk=lesson.course.pk)


class TakeQuizView(LoginRequiredMixin, View):
    """
    يعرض نموذج الاختبار ويعالج تقديم الإجابات.
    """
    def get(self, request, *args, **kwargs):
        quiz = get_object_or_404(Quiz.objects.prefetch_related('questions__choices'), pk=kwargs['pk'])
        submission = QuizSubmission.objects.filter(student=request.user, quiz=quiz).first()
        if submission:
            return redirect('courses:quiz_result', pk=submission.pk)
        return render(request, 'courses/quiz_form.html', {'quiz': quiz})

    def post(self, request, *args, **kwargs):
        quiz = get_object_or_404(Quiz.objects.prefetch_related('questions__choices'), pk=kwargs['pk'])
        
        # Unpack the tuple returned by the helper method correctly.
        score, _ = self.calculate_score(request.POST, quiz)
        
        submission, _ = QuizSubmission.objects.get_or_create(
            student=request.user, quiz=quiz, defaults={'score': score}
        )
        return redirect('courses:quiz_result', pk=submission.pk)
    
    @staticmethod
    def calculate_score(post_data, quiz):
        """دالة مساعدة لفصل منطق حساب الدرجة."""
        correct_answers = 0
        questions = quiz.questions.all()
        total_questions = questions.count()
        for question in questions:
            selected_choice_id = post_data.get(f'question_{question.pk}')
            if selected_choice_id:
                correct_choice = next((c for c in question.choices.all() if c.is_correct), None)
                if correct_choice and int(selected_choice_id) == correct_choice.id:
                    correct_answers += 1
        score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        return score, correct_answers


class QuizResultView(LoginRequiredMixin, DetailView):
    """
    يعرض نتيجة اختبار معينة بأمان، مع حسابات لعرض المخطط الدائري.
    """
    model = QuizSubmission
    template_name = 'courses/quiz_result.html'
    context_object_name = 'submission'
    pk_url_kwarg = 'pk'

    def get_queryset(self):
        """
        إصلاح أمني حرج: يضمن أن المستخدم لا يمكنه رؤية إلا نتائجه الخاصة.
        """
        queryset = super().get_queryset()
        return queryset.filter(student=self.request.user)
    
    def get_context_data(self, **kwargs):
        """
        يضيف تحليل الأداء والحسابات اللازمة للمخطط الدائري.
        """
        context = super().get_context_data(**kwargs)
        submission = self.object
        
        total_questions = submission.quiz.questions.count()
        correct_answers = round((submission.score / 100) * total_questions) if total_questions > 0 else 0
        
        # Calculations for the SVG donut chart are done here, not in the template.
        radius = 80
        circumference = 2 * math.pi * radius
        stroke_dashoffset = circumference * (1 - (submission.score / 100))

        context.update({
            'total_questions': total_questions,
            'correct_answers': correct_answers,
            'wrong_answers': total_questions - correct_answers,
            'circumference': circumference,
            'stroke_dashoffset': stroke_dashoffset,
        })
        return context