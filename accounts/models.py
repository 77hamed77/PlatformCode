# accounts/models.py

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class CustomUser(AbstractUser):
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

    def get_solved_problems_count(self):
        """
        Efficiently counts the number of unique problems solved by the user.
        Uses the correct related_name 'submissions'.
        """
        return self.submissions.filter(status='Correct').values('problem').distinct().count()