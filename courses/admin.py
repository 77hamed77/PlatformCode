# courses/admin.py

from django.contrib import admin
# CRITICAL FIX: Import the 'Count' aggregation function
from django.db.models import Count 
from .models import (
    LearningPath, Course, Module, Lesson,
    Quiz, Question, Choice, StudentProgress, QuizSubmission
)

# =================================================================
# Inlines - For a nested and integrated admin experience
# =================================================================

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 1
    min_num = 2
    max_num = 5


class QuestionInline(admin.StackedInline):
    model = Question
    inlines = [ChoiceInline]
    extra = 1
    show_change_link = True


class QuizInline(admin.StackedInline):
    model = Quiz
    show_change_link = True


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ('title', 'order')
    show_change_link = True


class ModuleInline(admin.StackedInline):
    model = Module
    inlines = [LessonInline]
    extra = 1
    show_change_link = True
    
# =================================================================
# ModelAdmins - For customizing the main admin pages
# =================================================================

@admin.register(LearningPath)
class LearningPathAdmin(admin.ModelAdmin):
    list_display = ('title', 'course_count')
    search_fields = ('title',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(course_count=Count('courses'))
        return queryset

    @admin.display(description="عدد الكورسات", ordering='course_count')
    def course_count(self, obj):
        return obj.course_count


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'learning_path', 'instructor', 'order', 'modules_count', 'lessons_count')
    list_filter = ('learning_path', 'instructor')
    search_fields = ('title', 'description')
    list_editable = ('order',)
    inlines = [ModuleInline]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('learning_path', 'instructor').annotate(
            modules_count=Count('modules', distinct=True),
            lessons_count=Count('modules__lessons', distinct=True)
        )
        return queryset

    @admin.display(description="عدد الوحدات", ordering='modules_count')
    def modules_count(self, obj):
        return obj.modules_count

    @admin.display(description="إجمالي الدروس", ordering='lessons_count')
    def lessons_count(self, obj):
        return obj.lessons_count


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    list_filter = ('course__learning_path', 'course')
    search_fields = ('title',)
    list_editable = ('order',)
    inlines = [LessonInline, QuizInline]
    list_select_related = ('course',)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'course', 'order')
    list_filter = ('module__course__learning_path', 'module__course')
    search_fields = ('title', 'content')
    list_editable = ('order',)
    list_select_related = ('module', 'course')


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'question_count')
    inlines = [QuestionInline]
    list_select_related = ('module',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(question_count=Count('questions'))
        return queryset
    
    @admin.display(description="عدد الأسئلة", ordering='question_count')
    def question_count(self, obj):
        return obj.question_count


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz', 'choices_count')
    inlines = [ChoiceInline]
    list_select_related = ('quiz',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(choices_count=Count('choices'))
        return queryset

    @admin.display(description="عدد الخيارات", ordering='choices_count')
    def choices_count(self, obj):
        return obj.choices_count


# Register read-only models for inspection
@admin.register(StudentProgress)
class StudentProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'lesson', 'completed_at')
    list_select_related = ('student', 'lesson')
    
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False


@admin.register(QuizSubmission)
class QuizSubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'quiz', 'score', 'submitted_at')
    list_select_related = ('student', 'quiz')
    
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False