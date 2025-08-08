# telegram_bot/utils.py

import asyncio
import telegram
from django.conf import settings
from asgiref.sync import async_to_sync

# ننشئ نسخة واحدة من البوت لاستخدامها في كل مكان
# هذا أفضل للأداء من إنشاء كائن بوت جديد مع كل رسالة
bot = telegram.Bot(token=settings.TELEGRAM_BOT_TOKEN)

def send_telegram_message(chat_id: str, message: str):
    """
    دالة مساعدة متزامنة (sync) لإرسال رسائل Telegram.
    تقوم بتغليف الاستدعاء غير المتزامن (async) بأمان.
    """
    if not chat_id:
        return
    
    try:
        # async_to_sync هو الجسر الذي يسمح لنا باستدعاء دالة async من كود sync (مثل الإشارات)
        async_to_sync(bot.send_message)(chat_id=chat_id, text=message, parse_mode='HTML')
    except Exception as e:
        print(f"Failed to send Telegram message to chat_id {chat_id}. Error: {e}")