# courses/templatetags/course_extras.py

from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """
    يقوم بضرب القيمة في الوسيط.
    الاستخدام: {{ value|multiply:arg }}
    مثال: {{ 5|multiply:3 }} -> 15
    """
    try:
        # نتأكد من أننا نتعامل مع أرقام
        return int(value) * int(arg)
    except (ValueError, TypeError):
        # في حالة وجود خطأ، نعيد القيمة الأصلية أو قيمة افتراضية
        return value