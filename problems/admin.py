# problems/admin.py

from django.contrib import admin
from django.db.models import Count
from .models import Problem, TestCase, Submission

# =================================================================
# Inlines - For a nested and integrated admin experience
# =================================================================

class TestCaseInline(admin.TabularInline):
    """
    Allows managing test cases directly from the Problem admin page.
    TabularInline is more compact and suitable for test cases.
    """
    model = TestCase
    extra = 1
    min_num = 1  # 1. FIX (Data Integrity): A problem must have at least one test case.
    

# =================================================================
# ModelAdmins - For customizing the main admin pages
# =================================================================

@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    """
    Admin view for the Problem model.
    """
    list_display = ('title', 'difficulty', 'points', 'test_case_count')
    list_filter = ('difficulty',)
    search_fields = ('title', 'description')
    inlines = [TestCaseInline]

    # 2. FIX (Performance): Annotate to get test case count efficiently.
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(test_case_count=Count('test_cases'))
        return queryset

    def test_case_count(self, obj):
        return obj.test_case_count
    test_case_count.short_description = "عدد حالات الاختبار"
    test_case_count.admin_order_field = 'test_case_count'


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    """
    Admin view for the Submission model.
    Designed for efficient viewing and analysis of historical data.
    """
    # 3. FIX (UX): Added more useful columns for better overview.
    list_display = ('problem', 'student', 'status', 'submitted_at')
    
    # 4. FIX (Performance): `list_select_related` is crucial for performance here.
    # It fetches the related problem and student in a single query.
    list_select_related = ('problem', 'student')
    
    # 5. FIX (UX): Added powerful filtering and search capabilities.
    list_filter = ('status', 'problem__difficulty', 'problem')
    search_fields = ('student__username', 'problem__title')
    date_hierarchy = 'submitted_at' # Adds intuitive date-based navigation

    # 6. CRITICAL FIX (Data Integrity): Make all fields read-only.
    # A submission is a historical record and should never be altered.
    def get_readonly_fields(self, request, obj=None):
        # If the object already exists, make all its fields read-only.
        if obj:
            return [field.name for field in self.model._meta.fields]
        return []

    # Disable the "Add submission" button in the admin
    def has_add_permission(self, request, obj=None):
        return False

    # Disable the "Delete submission" action (optional, but recommended)
    def has_delete_permission(self, request, obj=None):
        # Allow deletion only for superusers for maintenance purposes
        return request.user.is_superuser