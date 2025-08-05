# dashboard/models.py

from django.conf import settings
from django.db import models
from django.utils.html import strip_tags
from django.utils.text import Truncator


class TaskManager(models.Manager):
    """
    1. BEST PRACTICE: A custom Manager to provide reusable querysets.
    This helps keep views extremely clean.
    """
    def for_user(self, user):
        """Returns all tasks for a given user, correctly ordered."""
        return self.filter(student=user).order_by('is_completed', '-created_at')

    def incomplete_tasks_for_user(self, user):
        """Returns only the incomplete tasks for a user."""
        return self.for_user(user).filter(is_completed=False)

    def completed_tasks_for_user(self, user):
        """Returns only the completed tasks for a user."""
        return self.for_user(user).filter(is_completed=True)


class Task(models.Model):
    """
    Represents a single to-do item for a student.
    """
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="الطالب",
        # 2. FIX (Performance): Add a related_name for cleaner reverse lookups.
        related_name="tasks" 
    )
    # 3. FIX (Data Integrity): `blank=False` ensures titles are never empty.
    title = models.CharField("عنوان المهمة", max_length=255, blank=False)
    is_completed = models.BooleanField("مكتملة", default=False, db_index=True)
    created_at = models.DateTimeField("تاريخ الإنشاء", auto_now_add=True)

    # Attach the custom manager
    objects = TaskManager()

    class Meta:
        verbose_name = "مهمة"
        verbose_name_plural = "المهام"
        # Ordering is now handled by the manager for more flexibility
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    # 4. HELPER METHOD: Encapsulates the logic for toggling status.
    def toggle(self):
        """Toggles the completion status of the task."""
        self.is_completed = not self.is_completed
        self.save(update_fields=['is_completed'])


class Note(models.Model):
    """
    Represents a private note or idea for a student. Supports Markdown.
    """
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="الطالب",
        related_name="notes"
    )
    title = models.CharField("عنوان المذكرة", max_length=255, blank=False)
    content = models.TextField("المحتوى")
    created_at = models.DateTimeField("تاريخ الإنشاء", auto_now_add=True)
    updated_at = models.DateTimeField("آخر تحديث", auto_now=True)

    class Meta:
        verbose_name = "مذكرة"
        verbose_name_plural = "المذكرات"
        ordering = ['-updated_at']

    def __str__(self):
        return self.title

    # 5. HELPER METHOD: Provides a safe, plain-text snippet of the note content.
    def get_snippet(self, words=20):
        """
        Returns a truncated, plain-text version of the note's content.
        This is useful for list views and previews.
        """
        # strip_tags is important for security if markdown allows raw HTML
        plain_content = strip_tags(self.content)
        return Truncator(plain_content).words(words, truncate=' ...')