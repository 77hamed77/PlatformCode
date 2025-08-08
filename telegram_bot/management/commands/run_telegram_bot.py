# telegram_bot/management/commands/run_telegram_bot.py

from django.core.management.base import BaseCommand
from django.conf import settings
from telegram.ext import Application, CommandHandler
from telegram_bot import handlers # استيراد معالجات الأوامر من ملف handlers.py

class Command(BaseCommand):
    help = 'Runs the Telegram bot in polling mode.'

    def handle(self, *args, **options):
        
        token = settings.TELEGRAM_BOT_TOKEN
        if not token:
            self.stdout.write(self.style.ERROR("TELEGRAM_BOT_TOKEN is not configured in settings."))
            return

        self.stdout.write(self.style.SUCCESS("Starting Telegram bot..."))
        
        # إنشاء التطبيق
        application = Application.builder().token(token).build()

        # تسجيل معالجات الأوامر
        application.add_handler(CommandHandler("start", handlers.start_command))
        application.add_handler(CommandHandler("connect", handlers.connect_command))
        application.add_handler(CommandHandler("stats", handlers.stats_command))
        application.add_handler(CommandHandler("help", handlers.help_command))

        # بدء تشغيل البوت
        # run_polling يبقي البوت يعمل ويستمع للرسائل الجديدة
        application.run_polling()
        
        self.stdout.write(self.style.WARNING("Bot has been stopped."))