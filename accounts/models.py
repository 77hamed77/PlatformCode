# accounts/models.py

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.templatetags.static import static
import uuid
from django.conf import settings


class CustomUser(AbstractUser):
    """
    Extends the default Django User model.
    This model is the central point for all user-related data.
    """
    # --- Profile & Personalization ---
    AVATAR_CHOICES = (
        ('m1', 'ذكر 1'), ('m2', 'ذكر 2'), ('m3', 'ذكر 3'),
        ('f1', 'أنثى 1'), ('f2', 'أنثى 2'), ('f3', 'أنثى 3'),
    )
    avatar = models.CharField(
        "الصورة الرمزية",
        max_length=2,
        choices=AVATAR_CHOICES,
        default='m1'
    )

    # --- Role Management ---
    is_moderator = models.BooleanField(
        "مشرف",
        default=False,
        help_text="يحدد ما إذا كان يمكن للمستخدم الإشراف على المحتوى مثل غرف النقاش."
    )
    
    # --- Academic Information ---
    academic_year = models.PositiveIntegerField(
        verbose_name="السنة الدراسية",
        validators=[MinValueValidator(1), MaxValueValidator(6)],
        null=True,
        blank=True,
        help_text="السنة الدراسية للطالب (من 1 إلى 6)."
    )
    path = models.CharField(
        verbose_name="المسار المختار",
        max_length=100,
        blank=True,
        help_text="المسار التعليمي المفضل للطالب، مثل (تطوير الويب)."
    )

    # --- Gamification ---
    score = models.PositiveIntegerField(
        verbose_name="النقاط",
        default=0,
        db_index=True,
        help_text="مجموع النقاط التي حصل عليها المستخدم."
    )

    class Meta:
        ordering = ['-score', 'username']
        verbose_name = "مستخدم"
        verbose_name_plural = "المستخدمون"

    def __str__(self):
        return self.username

    # --- Helper Methods ---
    def get_avatar_url(self):
        """Returns the static path to the user's chosen avatar."""
        return static(f'images/avatars/{self.avatar}.jpg')

    def get_solved_problems_count(self):
        """Efficiently counts the number of unique problems solved by the user."""
        return self.submissions.filter(status='Correct').values('problem').distinct().count()
    


class TelegramLink(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='telegram_link')
    telegram_chat_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    connection_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {'Active' if self.is_active else 'Pending'}"