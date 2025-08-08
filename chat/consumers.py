# chat/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatRoom, ChatMessage

online_users = {}

class ChatConsumer(AsyncWebsocketConsumer):
    # ... (دالة connect و disconnect تبقى كما هي) ...
    async def connect(self):
        self.room_slug = self.scope['url_route']['kwargs']['room_slug']
        self.room_group_name = f'chat_{self.room_slug}'
        self.user = self.scope['user']

        if not self.user.is_authenticated:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        await self.add_user_to_online_list()
        await self.send_online_user_list()

    async def disconnect(self, close_code):
        await self.remove_user_from_online_list()
        await self.send_online_user_list()
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)


    # 1. تحديث دالة receive لتفهم أنواعًا مختلفة من الرسائل
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        user = self.scope['user']

        if not user.is_authenticated:
            return

        if message_type == 'chat_message':
            message_content = text_data_json['message']
            await self.save_message(user, message_content)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message_content,
                    'username': user.username
                }
            )
        elif message_type == 'typing':
            # 2. إرسال إشارة الكتابة إلى الآخرين في المجموعة
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_typing', # يستدعي دالة user_typing
                    'username': user.username,
                    'is_typing': text_data_json['is_typing']
                }
            )

    # ... (دالة chat_message و online_user_list تبقى كما هي) ...
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'username': event['username']
        }))

    async def online_user_list(self, event):
        await self.send(text_data=json.dumps({
            'type': 'online_user_list',
            'users': event['users']
        }))
        
    # 3. دالة جديدة للتعامل مع إشارات الكتابة
    async def user_typing(self, event):
        # إرسال إشارة الكتابة إلى WebSocket (المتصفح)
        await self.send(text_data=json.dumps({
            'type': 'user_typing',
            'username': event['username'],
            'is_typing': event['is_typing']
        }))

    # ... (بقية الدوال تبقى كما هي) ...
    async def add_user_to_online_list(self):
        if self.room_group_name not in online_users: online_users[self.room_group_name] = set()
        online_users[self.room_group_name].add(self.user.username)

    async def remove_user_from_online_list(self):
        if self.room_group_name in online_users: online_users[self.room_group_name].discard(self.user.username)

    async def send_online_user_list(self):
        users = list(online_users.get(self.room_group_name, set()))
        await self.channel_layer.group_send(self.room_group_name, {'type': 'online_user_list', 'users': users})

    @database_sync_to_async
    def save_message(self, user, message_content):
        room = ChatRoom.objects.get(slug=self.room_slug)
        ChatMessage.objects.create(room=room, author=user, content=message_content)