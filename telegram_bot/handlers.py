# telegram_bot/handlers.py

from telegram import Update
from telegram.ext import ContextTypes
from asgiref.sync import sync_to_async
from accounts.models import TelegramLink, CustomUser

# نستخدم sync_to_async لأن مكتبة python-telegram-bot غير متزامنة (async)
# بينما Django ORM متزامن (sync). هذا يسمح لنا باستدعاء كود Django بأمان.

@sync_to_async
def _get_or_create_telegram_link(user):
    # نستخدم get_or_create لضمان وجود سجل ربط لكل مستخدم يحاول الحصول على رمز
    link, _ = TelegramLink.objects.get_or_create(user=user)
    return link

@sync_to_async
def _connect_user_by_token(token, chat_id):
    try:
        # نبحث عن سجل ربط يحتوي على الرمز الصحيح ولم يتم تفعيله بعد
        link = TelegramLink.objects.get(connection_token=token, is_active=False)
        link.telegram_chat_id = chat_id
        link.is_active = True
        link.save(update_fields=['telegram_chat_id', 'is_active'])
        return f"تم ربط حسابك بنجاح! مرحبًا يا {link.user.username}."
    except TelegramLink.DoesNotExist:
        return "الرمز غير صالح أو تم استخدامه من قبل. يرجى طلب رمز جديد من لوحة التحكم."
    except Exception:
        return "حدث خطأ غير متوقع أثناء محاولة ربط الحساب."

@sync_to_async
def _get_user_stats(chat_id):
    try:
        link = TelegramLink.objects.select_related('user').get(telegram_chat_id=chat_id, is_active=True)
        user = link.user
        solved_problems = user.get_solved_problems_count()
        completed_lessons = user.progress_records.count()
        
        return (
            f"📊 إحصائياتك يا {user.username}:\n"
            f"🏆 النقاط: {user.score}\n"
            f"💻 المسائل المحلولة: {solved_problems}\n"
            f"📚 الدروس المكتملة: {completed_lessons}"
        )
    except TelegramLink.DoesNotExist:
        return "حسابك غير مرتبط. يرجى استخدام أمر /connect لربط حسابك أولاً."


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /start command."""
    welcome_message = (
        "أهلاً بك في بوت منصة كود!\n\n"
        "لربط حسابك وتلقي الإشعارات، اتبع الخطوات التالية:\n"
        "1. اذهب إلى 'لوحة التحكم' في حسابك على المنصة.\n"
        "2. ابحث عن قسم 'ربط Telegram' وانسخ أمر الربط.\n"
        "3. الصق الأمر هنا وأرسله.\n\n"
        "الأوامر المتاحة:\n"
        "/stats - لعرض إحصائياتك\n"
        "/help - لعرض هذه الرسالة"
    )
    await update.message.reply_text(welcome_message)


async def connect_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /connect <token> command."""
    if not context.args:
        await update.message.reply_text("الاستخدام غير صحيح. يرجى إرسال الأمر بالشكل التالي: /connect <الرمز_الخاص_بك>")
        return
        
    token = context.args[0]
    chat_id = update.message.chat_id
    reply_message = await _connect_user_by_token(token, chat_id)
    await update.message.reply_text(reply_message)


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /stats command."""
    chat_id = update.message.chat_id
    stats_message = await _get_user_stats(chat_id)
    await update.message.reply_text(stats_message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /help command."""
    await start_command(update, context) # It's the same message