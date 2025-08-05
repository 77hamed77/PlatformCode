# gamification/signals.py

from django.db import transaction
from django.db.models import F
from django.db.models.signals import post_save
from django.dispatch import receiver

# 1. FIX: Import all relevant models
from courses.models import StudentProgress, QuizSubmission
from problems.models import Submission as ProblemSubmission
from .utils import award_points # We will create this utility function

# 2. BEST PRACTICE: Centralized signal handlers for all gamification logic.

@receiver(post_save, sender=StudentProgress)
def award_points_on_lesson_completion(sender, instance, created, **kwargs):
    """
    Awards points when a student completes a lesson for the first time.
    """
    if created:
        # 3. BEST PRACTICE: Points can be defined on the lesson/course model for flexibility
        points = instance.lesson.points or 10 # Assuming a 'points' field on Lesson model
        award_points(student=instance.student, points=points)
        print(f"Awarded {points} points to {instance.student.username} for completing a lesson.")


@receiver(post_save, sender=QuizSubmission)
def award_points_on_quiz_submission(sender, instance, created, **kwargs):
    """
    Awards points based on quiz score for the first submission.
    """
    # Award points only on the first attempt
    if created and instance.score > 0:
        points = int(instance.score / 10) # Example: 10 points for a perfect score
        if points > 0:
            award_points(student=instance.student, points=points)
            print(f"Awarded {points} points to {instance.student.username} for quiz performance.")


@receiver(post_save, sender=ProblemSubmission)
def award_points_on_correct_submission(sender, instance, created, **kwargs):
    """
    Awards points when a student solves a problem correctly for the first time.
    """
    if created and instance.status == 'Correct':
        # Check if this is the first correct submission for this problem by this student
        is_first_correct_solve = not ProblemSubmission.objects.filter(
            student=instance.student,
            problem=instance.problem,
            status='Correct'
        ).exclude(pk=instance.pk).exists()

        if is_first_correct_solve:
            points = instance.problem.points
            award_points(student=instance.student, points=points)
            print(f"Awarded {points} points to {instance.student.username} for solving a problem.")