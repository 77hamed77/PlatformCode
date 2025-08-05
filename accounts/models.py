# accounts/models.py

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class CustomUser(AbstractUser):
    """
    Extends the default Django User model.
    This model is the central point for all user-related data.
    """
    
    # --- Academic Information ---
    # 1. FIX: Added validators to ensure data integrity.
    academic_year = models.PositiveIntegerField(
        verbose_name="السنة الدراسية",
        validators=[MinValueValidator(1), MaxValueValidator(6)],
        null=True,  # null is acceptable for numbers if it's truly optional
        blank=True, # Allows the field to be blank in forms
        help_text="السنة الدراسية للطالب (من 1 إلى 6)."
    )
    
    # 2. FIX: Removed `null=True` as per Django best practices for CharFields.
    # `blank=True` is sufficient, and the default will be an empty string ''.
    path = models.CharField(
        verbose_name="المسار المختار",
        max_length=100,
        blank=True,
        help_text="المسار التعليمي المفضل للطالب، مثل (تطوير الويب)."
    )

    # --- Gamification ---
    # 3. FIX: Added an index for faster ordering in leaderboards.
    score = models.PositiveIntegerField(
        verbose_name="النقاط",
        default=0,
        db_index=True, # Speeds up queries that order by score
        help_text="مجموع النقاط التي حصل عليها المستخدم."
    )

    # 4. BEST PRACTICE: Added a Meta class for ordering and verbose names.
    class Meta:
        ordering = ['-score', 'username']
        verbose_name = "مستخدم"
        verbose_name_plural = "المستخدمون"

    def __str__(self):
        """
        Returns the username for a more readable representation in the admin panel.
        """
        return self.username

    # 5. HELPER METHOD: Example of a useful method to centralize logic.
    def get_solved_problems_count(self):
        """
        Efficiently counts the number of unique problems solved by the user.
        - This avoids placing this logic repeatedly in different views.
        - The related_name 'submission_set' is automatically created by Django.
        """
        return self.submission_set.filter(status='Correct').values('problem').distinct().count()