# chat/admin.py
from django.contrib import admin
from .models import ChatRoom, ChatMessage

class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'learning_path')
    prepopulated_fields = {'slug': ('name',)} # يقوم بملء الـ slug تلقائيًا من الاسم

admin.site.register(ChatRoom, ChatRoomAdmin)
admin.site.register(ChatMessage)