# ai_tutor/models.py

from django.db import models
from django.conf import settings

class TutorConversation(models.Model):
    """يمثل محادثة كاملة بين طالب والمساعد الذكي."""
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tutor_conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"محادثة مع {self.student.username} في {self.created_at.strftime('%Y-%m-%d')}"

class TutorMessage(models.Model):
    """يمثل رسالة واحدة داخل محادثة."""
    conversation = models.ForeignKey(TutorConversation, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    is_from_ai = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        actor = "AI" if self.is_from_ai else "Student"
        return f"{actor}: {self.content[:50]}"