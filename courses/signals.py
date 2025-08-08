# courses/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver

# استيراد النماذج من جميع التطبيقات ذات الصلة
from .models import StudentProgress, QuizSubmission
from problems.models import Submission as ProblemSubmission
from gamification.models import Badge, StudentBadge # <-- استيراد نماذج الشارات

# استيراد الدالة المساعدة الآمنة
from .utils import award_points_safely

# =================================================================
# Central Badge Awarding Logic
# =================================================================

def check_and_award_badges(student):
    """
    دالة مركزية للتحقق من جميع الإنجازات المحتملة للطالب ومنح الشارات.
    يتم استدعاؤها بعد أي حدث قد يؤدي إلى إنجاز.
    """
    # جلب الشارات التي يملكها الطالب بالفعل لتجنب الاستعلامات المتكررة
    current_badge_ids = set(student.badges.values_list('badge_id', flat=True))

    # 1. التحقق من إنجازات حل المسائل
    solved_count = student.get_solved_problems_count()
    problem_badges = Badge.objects.filter(
        achievement_type=Badge.AchievementType.PROBLEMS, 
        threshold__lte=solved_count
    ).exclude(id__in=current_badge_ids) # جلب الشارات الجديدة فقط

    # 2. التحقق من إنجازات إكمال الدروس
    lessons_count = student.progress_records.count()
    lesson_badges = Badge.objects.filter(
        achievement_type=Badge.AchievementType.LESSONS, 
        threshold__lte=lessons_count
    ).exclude(id__in=current_badge_ids)

    # (يمكنك إضافة أنواع أخرى هنا، مثل الاختبارات)

    # دمج كل الشارات الجديدة التي يستحقها الطالب
    all_new_badges = list(problem_badges) + list(lesson_badges)
    
    # منح الشارات الجديدة
    for badge in all_new_badges:
        StudentBadge.objects.create(student=student, badge=badge)
        print(f"🎉 تهانينا! {student.username} حصل على شارة: '{badge.title}'")


# =================================================================
# Signal Handlers for Gamification (Points + Badges)
# =================================================================

@receiver(post_save, sender=StudentProgress)
def on_lesson_completion(sender, instance, created, **kwargs):
    """
    يمنح نقاطًا وشارات عند إكمال درس لأول مرة.
    """
    if created:
        points_to_award = 10
        award_points_safely(instance.student, points_to_award)
        # بعد منح النقاط، تحقق من أي شارات جديدة
        check_and_award_badges(instance.student)


@receiver(post_save, sender=QuizSubmission)
def on_quiz_submission(sender, instance, created, **kwargs):
    """
    يمنح نقاطًا وشارات بناءً على درجة الاختبار في المحاولة الأولى.
    """
    if created and instance.score > 0:
        points_to_award = int(instance.score / 10)
        if points_to_award > 0:
            award_points_safely(instance.student, points_to_award)
            # (يمكن إضافة منطق شارات الاختبارات هنا في المستقبل)
            # check_and_award_badges(instance.student)


@receiver(post_save, sender=ProblemSubmission)
def on_correct_submission(sender, instance, created, **kwargs):
    """
    يمنح نقاطًا وشارات عند حل مسألة بشكل صحيح لأول مرة.
    """
    if created and instance.status == 'Correct':
        is_first_correct = not ProblemSubmission.objects.filter(
            student=instance.student,
            problem=instance.problem,
            status='Correct'
        ).exclude(pk=instance.pk).exists()

        if is_first_correct:
            points_to_award = instance.problem.points
            award_points_safely(instance.student, points_to_award)
            # بعد منح النقاط، تحقق من أي شارات جديدة
            check_and_award_badges(instance.student)