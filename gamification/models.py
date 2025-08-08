# gamification/models.py
from django.db import models
from django.conf import settings

class Badge(models.Model):
    title = models.CharField("عنوان الشارة", max_length=255, unique=True)
    description = models.TextField("وصف الإنجاز")
    icon = models.CharField("أيقونة (Emoji أو اسم أيقونة)", max_length=50, help_text="مثال: 🎓 أو 'code-branch'")
    
    # نوع الإنجاز (لتسهيل البرمجة لاحقًا)
    class AchievementType(models.TextChoices):
        LESSONS = 'LESSONS', 'إكمال الدروس'
        PROBLEMS = 'PROBLEMS', 'حل المسائل'
        TESTS = 'TESTS', 'اجتياز الاختبارات'
    
    achievement_type = models.CharField("نوع الإنجاز", max_length=20, choices=AchievementType.choices)
    threshold = models.PositiveIntegerField("العدد المطلوب", help_text="مثال: حل 10 مسائل")

    def __str__(self):
        return self.title

class StudentBadge(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="badges")
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    awarded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'badge') # الطالب لا يمكن أن يحصل على نفس الشارة مرتين