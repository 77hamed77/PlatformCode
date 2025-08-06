# courses/models.py

from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError


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
    order = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        verbose_name = "كورس"
        verbose_name_plural = "الكورسات"
        ordering = ['order']
        unique_together = ('learning_path', 'title')

    def __str__(self):
        return self.title

    def get_lessons_count(self):
        return self.lessons.count()


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
        if not self.course_id:
            self.course = self.module.course
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Quiz(models.Model):
    module = models.OneToOneField(Module, related_name='quiz', on_delete=models.CASCADE, verbose_name="الوحدة التابع لها")
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
    
    def clean(self):
        if self.is_correct:
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