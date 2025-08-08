# ai_tutor/services.py

import google.generativeai as genai
from django.conf import settings
from .models import TutorConversation, TutorMessage

class GeminiTutorService:
    """
    طبقة خدمة للتواصل مع Gemini AI.
    تقوم بتغليف منطق بناء الطلبات ومعالجة الاستجابات، وتدعم البث والوعي بالسياق.
    """
    def __init__(self):
        # التأكد من وجود مفتاح API قبل المتابعة
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not configured in settings.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def _prepare_history(self, conversation: TutorConversation):
        """
        يحضر سجل المحادثة بالتنسيق الذي يتوقعه Gemini.
        يجلب آخر 10 رسائل فقط لإبقاء السياق موجزًا وتوفير التكاليف.
        """
        history = []
        # جلب آخر 10 رسائل (5 أدوار محادثة)
        messages = conversation.messages.order_by('-timestamp').all()[:10]
        # إعادة ترتيبها بالترتيب الزمني الصحيح (من الأقدم إلى الأحدث)
        for msg in reversed(messages):
            role = 'model' if msg.is_from_ai else 'user'
            history.append({'role': role, 'parts': [msg.content]})
        return history

    def get_streaming_response(self, user_prompt: str, conversation: TutorConversation, context_info: str = ""):
        """
        دالة مولدة (generator) تقوم ببث أجزاء من استجابة Gemini، مع الأخذ في الاعتبار السياق.
        """
        system_prompt = """
        أنت "كود مساعد"، مدرس ذكاء اصطناعي ودود ومحفز في منصة "كود" التعليمية. مهمتك هي مساعدة طلاب الهندسة المعلوماتية.
        قواعدك هي:
        1. كن دائمًا مشجعًا وإيجابيًا.
        2. لا تعطِ الحل النهائي لمسألة برمجية مباشرة أبدًا. بدلاً من ذلك، قم بإعطاء تلميحات، اسأل أسئلة توجيهية، أو اشرح المفهوم الأساسي.
        3. إذا سُئلت عن مفهوم برمجي، اشرحه ببساطة ووضوح مع مثال قصير ومُنسَّق ككتلة برمجية باستخدام Markdown.
        4. خاطب الطالب دائمًا باحترام وود.
        """
        
        # إضافة السياق المستلم من الصفحة الحالية إلى شخصية النظام
        context_prompt = ""
        if context_info:
            context_prompt = f"\n\nمعلومات إضافية (سياق الصفحة الحالية للطالب، استخدمها بذكاء): {context_info}"

        # حفظ رسالة الطالب أولاً لبناء سجل المحادثة
        TutorMessage.objects.create(conversation=conversation, content=user_prompt, is_from_ai=False)
        history = self._prepare_history(conversation)
        chat_session = self.model.start_chat(history=history)

        try:
            full_prompt = f"{system_prompt}{context_prompt}\n\nسؤال الطالب الأخير هو: {user_prompt}"
            response_stream = chat_session.send_message(full_prompt, stream=True)
            
            full_ai_response = ""
            for chunk in response_stream:
                if chunk.text:
                    full_ai_response += chunk.text
                    yield chunk.text

            # بعد انتهاء البث، قم بحفظ الرسالة الكاملة للذكاء الاصطناعي في قاعدة البيانات
            if full_ai_response.strip():
                TutorMessage.objects.create(conversation=conversation, content=full_ai_response, is_from_ai=True)

        except Exception as e:
            error_message = f"عذرًا، حدث خطأ أثناء التواصل مع المساعد الذكي. قد يكون هناك ضغط على الخدمة. يرجى المحاولة مرة أخرى.\n\nتفاصيل الخطأ: {e}"
            TutorMessage.objects.create(conversation=conversation, content=error_message, is_from_ai=True)
            yield error_message

# إنشاء نسخة واحدة من الخدمة لإعادة استخدامها في المشروع
gemini_service = GeminiTutorService()