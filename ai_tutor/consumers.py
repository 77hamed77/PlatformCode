# ai_tutor/consumers.py

import json
import asyncio # <-- استيراد المكتبة الأساسية للعمليات غير المتزامنة
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import TutorConversation
from .services import gemini_service

class TutorConsumer(AsyncWebsocketConsumer):
    """
    Consumer للتعامل مع محادثات WebSocket مع المساعد الذكي.
    تم تحسينه الآن لدعم البث الحقيقي (real-time streaming).
    """
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
        else:
            await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        user_prompt = text_data_json.get('prompt', '')
        conversation_id = text_data_json.get('conversation_id')

        if not user_prompt:
            return

        conversation = await self.get_or_create_conversation(conversation_id)

        # --- CRITICAL FIX: The Real Streaming Implementation ---
        #
        # `asyncio.to_thread` يقوم بتشغيل الدالة البطيئة (gemini_service...) في خيط منفصل.
        # الأهم من ذلك، أنه يسمح لنا بالتعامل مع المولد (generator) الذي تعيده.
        # حلقة `for` التالية ستحصل على كل `chunk` فور أن يرسله Gemini، دون انتظار البقية.
        #
        stream_generator = await asyncio.to_thread(
            gemini_service.get_streaming_response,
            user_prompt,
            conversation
        )

        for chunk in stream_generator:
            await self.send(text_data=json.dumps({
                'type': 'chunk',
                'content': chunk
            }))
        
        # بعد انتهاء البث، إرسال رسالة النهاية
        await self.send(text_data=json.dumps({
            'type': 'end_of_stream',
            'conversation_id': conversation.id
        }))

    @database_sync_to_async
    def get_or_create_conversation(self, conversation_id):
        if conversation_id:
            try:
                return TutorConversation.objects.get(pk=conversation_id, student=self.user)
            except TutorConversation.DoesNotExist:
                pass
        return TutorConversation.objects.create(student=self.user)