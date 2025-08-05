# courses/models.py

from django.conf import settings
from django.db import models
from django.db.models import Count, Q
from django.core.exceptions import ValidationError


# =================================================================
# Core Content Models
# =================================================================

class LearningPath(models.Model):
    title = models.CharField("عنوان المسار", max_length=200, unique=True)
    description = models.TextField("وصف المسار")

    class Meta:
        verbose_name = "مسار تعليمي"
        verbose_name_plural = "المسارات التعليمية"
        ordering = ['title']

    def __str__(self):
        return self.title


class Course(models.Model):
    learning_path = models.ForeignKey(LearningPath, related_name='courses', on_delete=models.CASCADE, verbose_name="المسار التعليمي")
    title = models.CharField("عنوان الكورس", max_length=200)
    description = models.TextField("وصف الكورس")
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="المعلم")
    
    # 1. FIX (Performance): Using a dedicated library like `django-ordered-model` is the best
    # solution for ordering. For simplicity here, we'll keep `order` but add an index.
    order = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        verbose_name = "كورس"
        verbose_name_plural = "الكورسات"
        ordering = ['order']
        unique_together = ('learning_path', 'title') # Prevent duplicate course titles within the same path

    def __str__(self):
        return self.title

    # 2. HELPER METHOD: Centralizes logic, making views thinner.
    def get_lessons_count(self):
        """Efficiently calculates the total number of lessons in the course."""
        return Lesson.objects.filter(module__course=self).count()


class Module(models.Model):
    course = models.ForeignKey(Course, related_name='modules', on_delete=models.CASCADE, verbose_name="الكورس")
    title = models.CharField("عنوان الوحدة", max_length=200)
    description = models.TextField("وصف الوحدة", blank=True)
    order = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        verbose_name = "وحدة"
        verbose_name_plural = "الوحدات"
        ordering = ['order']
        unique_together = ('course', 'title')

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Lesson(models.Model):
    module = models.ForeignKey(Module, related_name='lessons', on_delete=models.CASCADE, verbose_name="الوحدة")
    
    # 3. FIX (Performance): Adding a direct ForeignKey to Course for simpler queries.
    # This is a form of denormalization for performance.
    course = models.ForeignKey(Course, related_name='lessons', on_delete=models.CASCADE, verbose_name="الكورس")
    
    title = models.CharField("عنوان الدرس", max_length=200)
    content = models.TextField("محتوى الدرس")
    video_url = models.URLField("رابط الفيديو", blank=True)
    order = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        verbose_name = "درس"
        verbose_name_plural = "الدروس"
        ordering = ['order']
        unique_together = ('module', 'title')

    def save(self, *args, **kwargs):
        """Overrides save to automatically set the course."""
        if not self.course_id:
            self.course = self.module.course
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


# =================================================================
# Quiz & Progress Models
# =================================================================

class Quiz(models.Model):
    module = models.OneToOneField(Module, on_delete=models.CASCADE, verbose_name="الوحدة التابع لها")
    title = models.CharField("عنوان الاختبار", max_length=255)

    class Meta:
        verbose_name = "اختبار"
        verbose_name_plural = "الاختبارات"

    def __str__(self):
        return self.title


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, related_name='questions', on_delete=models.CASCADE, verbose_name="الاختبار")
    text = models.TextField("نص السؤال")

    class Meta:
        verbose_name = "سؤال"
        verbose_name_plural = "الأسئلة"

    def __str__(self):
        return self.text[:50]


class Choice(models.Model):
    question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE, verbose_name="السؤال")
    text = models.CharField("نص الخيار", max_length=255)
    is_correct = models.BooleanField("هل هو الخيار الصحيح؟", default=False)

    class Meta:
        verbose_name = "خيار"
        verbose_name_plural = "الخيارات"
        unique_together = ('question', 'text')

    def __str__(self):
        return self.text
    
    # 4. CRITICAL FIX (Data Integrity): Ensures there is one and only one correct answer per question.
    def clean(self):
        """
        Custom validation to enforce business logic.
        This is called automatically by ModelForms (like in the admin).
        """
        if self.is_correct:
            # Check if there are other choices for the same question that are already correct.
            other_correct_choices = Choice.objects.filter(
                question=self.question, 
                is_correct=True
            ).exclude(pk=self.pk)
            
            if other_correct_choices.exists():
                raise ValidationError("لا يمكن وجود أكثر من إجابة صحيحة واحدة لهذا السؤال.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class StudentProgress(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='progress_records', on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'lesson')
        verbose_name = "تقدم الطالب"
        verbose_name_plural = "تقدم الطلاب"


class QuizSubmission(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.FloatField("الدرجة")
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'quiz')
        verbose_name = "نتيجة اختبار"
        verbose_name_plural = "نتائج الاختبارات"