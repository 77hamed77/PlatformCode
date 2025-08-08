# courses/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.conf import settings

# استيراد النماذج
from .models import StudentProgress, QuizSubmission, Course
from problems.models import Submission as ProblemSubmission

# استيراد أداة إرسال رسائل Telegram
# تأكد من أن هذا المسار صحيح بناءً على هيكل مشروعك
from telegram_bot.utils import send_telegram_message

# استيراد الدالة المساعدة الآمنة
# تأكد من أن هذا الملف موجود في courses/utils.py
from .utils import award_points_safely

# =================================================================
# Signal Handlers (No changes needed here)
# =================================================================
@receiver(post_save, sender=StudentProgress)
def on_lesson_completion(sender, instance, created, **kwargs):
    if created:
        points_to_award = 10
        award_points_safely(instance.student, points_to_award)

@receiver(post_save, sender=QuizSubmission)
def on_quiz_submission(sender, instance, created, **kwargs):
    if created and instance.score > 0:
        points_to_award = int(instance.score / 10)
        if points_to_award > 0:
            award_points_safely(instance.student, points_to_award)

@receiver(post_save, sender=ProblemSubmission)
def on_correct_submission(sender, instance, created, **kwargs):
    if created and instance.status == 'Correct':
        is_first_correct = not ProblemSubmission.objects.filter(student=instance.student, problem=instance.problem, status='Correct').exclude(pk=instance.pk).exists()
        if is_first_correct:
            points_to_award = instance.problem.points
            award_points_safely(instance.student, points_to_award)

# =================================================================
# Notification Signal Handler (This is where we debug)
# =================================================================

@receiver(post_save, sender=Course)
def on_new_course_created(sender, instance, created, **kwargs):
    """
    يرسل إشعار Telegram لجميع المستخدمين المرتبطين عند إنشاء كورس جديد.
    """
    # 1. Diagnostic Print: Check if the signal is firing at all.
    print("====== on_new_course_created SIGNAL FIRED ======")
    
    if created:
        print(f"  -> Course '{instance.title}' was CREATED.")
        from accounts.models import TelegramLink

        active_links = TelegramLink.objects.filter(is_active=True)
        
        # 2. Diagnostic Print: Check if we are finding any active users.
        print(f"  -> Found {active_links.count()} active Telegram link(s).")
        
        if not active_links.exists():
            print("  -> No active users to notify. Exiting.")
            return

        course_url = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000') + reverse('courses:course_detail', kwargs={'pk': instance.pk})
        
        message = (
            f"📢 <b>كورس جديد متاح!</b>\n\n"
            f"تمت إضافة كورس '<b>{instance.title}</b>' إلى مسار '<b>{instance.learning_path.title}</b>'.\n\n"
            f"<a href='{course_url}'>ابدأ التعلم الآن!</a>"
        )
        
        for link in active_links:
            # 3. Diagnostic Print: Check if we are attempting to send a message.
            print(f"  -> Attempting to send notification to user: {link.user.username} (Chat ID: {link.telegram_chat_id})")
            send_telegram_message(link.telegram_chat_id, message)
        
        print("====== SIGNAL FINISHED ======")
    else:
        print(f"  -> Course '{instance.title}' was UPDATED, not created. No notification sent.")
        print("====== SIGNAL FINISHED ======")