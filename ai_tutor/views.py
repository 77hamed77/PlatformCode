# ai_tutor/views.py

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View
from .services import gemini_service
from .models import TutorConversation

class AskAITutorView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        user_prompt = request.POST.get('prompt', '')
        conversation_id = request.POST.get('conversation_id')
        
        # 1. الحصول على المحادثة الحالية أو إنشاء واحدة جديدة
        if conversation_id:
            conversation = TutorConversation.objects.get(pk=conversation_id, student=request.user)
        else:
            conversation = TutorConversation.objects.create(student=request.user)

        # 2. الحصول على استجابة الذكاء الاصطناعي
        ai_response = gemini_service.get_response(user_prompt, conversation)

        context = {
            'user_message': user_prompt,
            'ai_message': ai_response,
            'conversation_id': conversation.id
        }
        # 3. إرجاع قالب جزئي جديد يحتوي على "دور" المحادثة بأكمله
        return render(request, 'ai_tutor/partials/conversation_turn.html', context)
    
