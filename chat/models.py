# chat/models.py

from django.db import models
from django.conf import settings
from courses.models import LearningPath

class ChatRoom(models.Model):
    name = models.CharField("اسم الغرفة", max_length=255)
    slug = models.SlugField("الرابط (slug)", unique=True)
    learning_path = models.ForeignKey(
        LearningPath,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="المسار التعليمي المرتبط"
    )

    def __str__(self):
        return self.name

class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, related_name='messages', on_delete=models.CASCADE, verbose_name="الغرفة")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='chat_messages', on_delete=models.CASCADE, verbose_name="المؤلف")
    content = models.TextField("المحتوى")
    timestamp = models.DateTimeField("التوقيت", auto_now_add=True, db_index=True)
    
    # --- Moderation Fields ---
    is_deleted = models.BooleanField("محذوفة", default=False)
    
    # --- Rich Content Fields ---
    is_code = models.BooleanField(default=False)
    link_url = models.URLField(blank=True, null=True)
    link_title = models.CharField(max_length=255, blank=True, null=True)
    link_description = models.TextField(blank=True, null=True)
    link_image = models.URLField(blank=True, null=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"رسالة من {self.author.username} في {self.room.name}"