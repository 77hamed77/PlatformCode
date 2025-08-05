# problems/models.py

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Problem(models.Model):
    """
    يمثل مسألة برمجية واحدة.
    - يستخدم TextChoices لضمان سلامة البيانات.
    - يحتوي على دوال مساعدة لعزل منطق العرض.
    """
    class Difficulty(models.TextChoices):
        EASY = 'Easy', 'سهل'
        MEDIUM = 'Medium', 'متوسط'
        HARD = 'Hard', 'صعب'

    title = models.CharField("عنوان المسألة", max_length=255, unique=True)
    description = models.TextField("وصف المسألة")
    difficulty = models.CharField(
        "مستوى الصعوبة",
        max_length=10,
        choices=Difficulty.choices,
        default=Difficulty.EASY,
        db_index=True  # فهرس لتسريع التصفية حسب الصعوبة
    )
    points = models.PositiveIntegerField("النقاط الممنوحة", default=10)

    class Meta:
        verbose_name = "مسألة"
        verbose_name_plural = "المسائل"
        ordering = ['points']

    def __str__(self):
        return self.title

    def get_difficulty_color_classes(self):
        """
        يعزل منطق العرض: يرجع فئات CSS المناسبة لشارة الصعوبة.
        """
        return {
            self.Difficulty.EASY: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300",
            self.Difficulty.MEDIUM: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300",
            self.Difficulty.HARD: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300",
        }.get(self.difficulty, "bg-gray-100 text-gray-800")


class TestCase(models.Model):
    """
    يمثل حالة اختبار واحدة لمسألة معينة.
    """
    problem = models.ForeignKey(Problem, related_name='test_cases', on_delete=models.CASCADE, verbose_name="المسألة")
    input_data = models.TextField("بيانات الإدخال", blank=True)
    expected_output = models.TextField("الناتج المتوقع")

    class Meta:
        verbose_name = "حالة اختبار"
        verbose_name_plural = "حالات الاختبار"

    def __str__(self):
        return f"حالة اختبار للمسألة: {self.problem.title}"


class Submission(models.Model):
    """
    يمثل تقديم كود واحد من طالب لمسألة.
    """
    class Status(models.TextChoices):
        PENDING = 'Pending', 'قيد المراجعة'
        CORRECT = 'Correct', 'إجابة صحيحة'
        WRONG = 'Wrong', 'إجابة خاطئة'
        ERROR = 'Error', 'خطأ تشغيلي'
    
    problem = models.ForeignKey(Problem, related_name='submissions', on_delete=models.CASCADE)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='submissions', on_delete=models.CASCADE)
    submitted_code = models.TextField("الكود المُقدَّم")
    status = models.CharField(
        "الحالة",
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True
    )
    submitted_at = models.DateTimeField("تاريخ التقديم", auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "تقديم"
        verbose_name_plural = "التقديمات"
        indexes = [
            models.Index(fields=['student', 'problem', 'status']), # فهرس مركب للاستعلامات الشائعة
        ]
        ordering = ['-submitted_at']

    def __str__(self):
        return f"تقديم من {self.student.username} لمسألة {self.problem.title}"
        
    def get_status_styles(self):
        """
        يعزل منطق العرض: يرجع قاموسًا يحتوي على فئات CSS وأيقونة SVG للحالة.
        """
        styles = {
            self.Status.CORRECT: {'bg': 'bg-green-50 dark:bg-green-900/50', 'text': 'text-green-700 dark:text-green-300', 'icon_text': 'text-green-500', 'icon_svg': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>'},
            self.Status.WRONG: {'bg': 'bg-red-50 dark:bg-red-900/50', 'text': 'text-red-700 dark:text-red-300', 'icon_text': 'text-red-500', 'icon_svg': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"></path>'},
        }
        default_style = {'bg': 'bg-yellow-50 dark:bg-yellow-900/50', 'text': 'text-yellow-700 dark:text-yellow-300', 'icon_text': 'text-yellow-500', 'icon_svg': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>'}
        return styles.get(self.status, default_style)