# dashboard/templatetags/markdown_extras.py

import markdown
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

register = template.Library()

# 1. امتداد مخصص لإضافة target="_blank" للروابط الخارجية
class LinkTargetExtension(markdown.extensions.Extension):
    """
    امتداد مخصص لمكتبة Markdown ليقوم تلقائيًا بإضافة
    target="_blank" و rel="noopener noreferrer" إلى جميع الروابط.
    """
    def extendMarkdown(self, md):
        # TreeProcessor هو ما يسمح لنا بالتعديل على شجرة HTML بعد إنشائها
        md.treeprocessors.register(LinkTargetProcessor(md), 'link_target', 15)

class LinkTargetProcessor(markdown.treeprocessors.Treeprocessor):
    def run(self, root):
        # ابحث عن جميع وسوم الروابط 'a' في المستند
        for element in root.iter("a"):
            # أضف السمات المطلوبة
            element.set("target", "_blank")
            element.set("rel", "noopener noreferrer")
        return root

@register.filter(name='markdownify') # استخدام name='markdownify' هو ممارسة جيدة
@stringfilter
def markdownify(value):
    """
    يقوم بتحويل نص مكتوب بلغة Markdown إلى HTML آمن للعرض مع ميزات إضافية:
    - تلوين الصيغة البرمجية (Syntax Highlighting).
    - فتح جميع الروابط في تبويب جديد تلقائيًا.
    """
    # 2. قائمة بالامتدادات لتنظيم أفضل
    extensions = [
        'fenced_code',  # لتفعيل كتل الكود باستخدام ```
        'codehilite',   # لتفعيل تلوين الصيغة داخل كتل الكود
        LinkTargetExtension(), # تفعيل الامتداد المخصص الذي أنشأناه
    ]
    
    html = markdown.markdown(value, extensions=extensions)
    
    return mark_safe(html)