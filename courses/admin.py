# courses/admin.py

from django.contrib import admin
from .models import (
    LearningPath, Course, Module, Lesson,
    Quiz, Question, Choice, StudentProgress, QuizSubmission
)

# =================================================================
# Inlines - For a nested and integrated admin experience
# =================================================================

class ChoiceInline(admin.TabularInline):
    """Allows adding choices directly within the Question admin page."""
    model = Choice
    extra = 1  # Start with one extra choice field
    min_num = 2  # A question must have at least 2 choices
    max_num = 5  # A question can have at most 5 choices


class QuestionInline(admin.StackedInline):
    """Allows adding questions and their choices directly within the Quiz admin page."""
    model = Question
    inlines = [ChoiceInline]
    extra = 1
    show_change_link = True # Allows quick navigation to the question's own admin page


class QuizInline(admin.StackedInline):
    """Allows creating a quiz directly within the Module admin page."""
    model = Quiz
    # We don't need to add questions here, it's better to manage them from the Quiz page.
    show_change_link = True


class LessonInline(admin.TabularInline):
    """Allows adding lessons directly within the Module admin page."""
    model = Lesson
    extra = 1
    fields = ('title', 'order') # Keep it simple, edit content on the lesson's own page
    show_change_link = True


class ModuleInline(admin.StackedInline):
    """
    CRITICAL FIX (UX): The core of the new experience.
    Allows managing all modules of a course from the course page itself.
    """
    model = Module
    inlines = [LessonInline] # Nesting lessons inside modules
    extra = 1
    show_change_link = True
    
# =================================================================
# ModelAdmins - For customizing the main admin pages
# =================================================================

@admin.register(LearningPath)
class LearningPathAdmin(admin.ModelAdmin):
    list_display = ('title', 'course_count')
    search_fields = ('title',)

    # 1. FIX (Performance): Annotate to get course count in a single query.
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(course_count=Count('courses'))
        return queryset

    def course_count(self, obj):
        return obj.course_count
    course_count.short_description = "عدد الكورسات"
    course_count.admin_order_field = 'course_count'


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'learning_path', 'instructor', 'order', 'modules_count', 'lessons_count')
    list_filter = ('learning_path', 'instructor')
    search_fields = ('title', 'description')
    list_editable = ('order',) # Allows quick reordering from the list view
    
    # 2. UX IMPROVEMENT: This is the main change for a better workflow.
    inlines = [ModuleInline]

    # 3. FIX (Performance): Use `select_related` and `annotate` for a super-fast list view.
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('learning_path', 'instructor').annotate(
            modules_count=Count('modules', distinct=True),
            lessons_count=Count('modules__lessons', distinct=True)
        )
        return queryset

    def modules_count(self, obj):
        return obj.modules_count
    modules_count.short_description = "عدد الوحدات"
    modules_count.admin_order_field = 'modules_count'

    def lessons_count(self, obj):
        return obj.lessons_count
    lessons_count.short_description = "إجمالي الدروس"
    lessons_count.admin_order_field = 'lessons_count'


# Note: We don't need a separate ModuleAdmin anymore if we manage them from CourseAdmin.
# However, it can be useful for direct access if needed.
@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    list_filter = ('course__learning_path', 'course')
    search_fields = ('title',)
    list_editable = ('order',)
    inlines = [LessonInline, QuizInline]
    
    # FIX (Performance)
    list_select_related = ('course',)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'course', 'order')
    list_filter = ('module__course__learning_path', 'module__course')
    search_fields = ('title', 'content')
    list_editable = ('order',)
    
    # FIX (Performance)
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
    
    def question_count(self, obj):
        return obj.question_count
    question_count.short_description = "عدد الأسئلة"


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz', 'choices_count')
    inlines = [ChoiceInline]
    list_select_related = ('quiz',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(choices_count=Count('choices'))
        return queryset

    def choices_count(self, obj):
        return obj.choices_count
    choices_count.short_description = "عدد الخيارات"


# Register read-only models for inspection
@admin.register(StudentProgress)
class StudentProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'lesson', 'completed_at')
    list_select_related = ('student', 'lesson')
    readonly_fields = ('student', 'lesson', 'completed_at')


@admin.register(QuizSubmission)
class QuizSubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'quiz', 'score', 'submitted_at')
    list_select_related = ('student', 'quiz')
    readonly_fields = ('student', 'quiz', 'score', 'submitted_at')