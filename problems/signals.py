# gamification/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver

# استيراد النماذج من جميع التطبيقات ذات الصلة
from courses.models import StudentProgress, QuizSubmission
from problems.models import Submission as ProblemSubmission
from .utils import award_points # استيراد الأداة المساعدة الآمنة

# =================================================================
# Signal Handlers for Gamification Events
# =================================================================

@receiver(post_save, sender=StudentProgress)
def on_lesson_completion(sender, instance, created, **kwargs):
    """Awards points when a student completes a lesson for the first time."""
    if created:
        points = getattr(instance.lesson, 'points', 10) # 10 is a fallback
        award_points(student=instance.student, points=points)

@receiver(post_save, sender=QuizSubmission)
def on_quiz_submission(sender, instance, created, **kwargs):
    """Awards points based on quiz score for the first submission."""
    if created and instance.score > 0:
        points = int(instance.score / 10)
        if points > 0:
            award_points(student=instance.student, points=points)

@receiver(post_save, sender=ProblemSubmission)
def on_problem_submission(sender, instance, created, **kwargs):
    """
    1. REFACTORED LOGIC: The signal handler for problem submissions.
    Awards points only on the first correct solve.
    """
    # Award points only on the first submission that is correct
    if created and instance.status == 'Correct':
        # 2. FIX (Efficiency): More efficient check for first-time solve.
        # This check is now robust and part of the centralized logic.
        is_first_correct_solve = not ProblemSubmission.objects.filter(
            student=instance.student,
            problem=instance.problem,
            status='Correct'
        ).exclude(pk=instance.pk).exists()

        if is_first_correct_solve:
            points = instance.problem.points
            award_points(student=instance.student, points=points)