# courses/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver

# استيراد النماذج من جميع التطبيقات ذات الصلة
from .models import StudentProgress, QuizSubmission
from problems.models import Submission as ProblemSubmission

# استيراد الدالة المساعدة الآمنة
from .utils import award_points_safely

# =================================================================
# Signal Handlers for Gamification
# =================================================================

@receiver(post_save, sender=StudentProgress)
def on_lesson_completion(sender, instance, created, **kwargs):
    """
    يمنح نقاطًا عند إكمال درس لأول مرة.
    """
    if created:
        # ملاحظة: في المستقبل، يمكنك إضافة حقل "points" إلى نموذج Lesson
        # points_to_award = instance.lesson.points
        points_to_award = 10  # قيمة ثابتة حاليًا
        award_points_safely(instance.student, points_to_award)


@receiver(post_save, sender=QuizSubmission)
def on_quiz_submission(sender, instance, created, **kwargs):
    """
    يمنح نقاطًا بناءً على درجة الاختبار في المحاولة الأولى.
    """
    if created and instance.score > 0:
        points_to_award = int(instance.score / 10)
        if points_to_award > 0:
            award_points_safely(instance.student, points_to_award)


@receiver(post_save, sender=ProblemSubmission)
def on_correct_submission(sender, instance, created, **kwargs):
    """
    يمنح نقاطًا عند حل مسألة بشكل صحيح لأول مرة.
    (تم نقل هذا المنطق هنا لمركزية نظام النقاط)
    """
    if created and instance.status == 'Correct':
        # تحقق مما إذا كان هذا هو الحل الصحيح الأول لهذه المسألة من قبل هذا الطالب
        is_first_correct = not ProblemSubmission.objects.filter(
            student=instance.student,
            problem=instance.problem,
            status='Correct'
        ).exclude(pk=instance.pk).exists()

        if is_first_correct:
            points_to_award = instance.problem.points
            award_points_safely(instance.student, points_to_award)