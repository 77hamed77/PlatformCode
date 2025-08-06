# courses/utils.py

from django.db import transaction
from django.db.models import F

def award_points_safely(student, points_to_award):
    """
    دالة آمنة ومركزية لمنح النقاط لمستخدم.
    - تمنع حالات السباق (Race Conditions) باستخدام F() expressions.
    - تضمن اتساق البيانات باستخدام معاملة ذرية (atomic transaction).
    """
    if not student or not points_to_award or points_to_award <= 0:
        return

    try:
        with transaction.atomic():
            # تحديث النقاط مباشرة في قاعدة البيانات لتجنب حالات السباق
            student.score = F('score') + points_to_award
            student.save(update_fields=['score'])
            
            # تحديث الكائن في ذاكرة Python ليعكس القيمة الجديدة فورًا
            student.refresh_from_db(fields=['score'])
            
            print(f"Awarded {points_to_award} points to {student.username}. New score: {student.score}")

    except Exception as e:
        # من الجيد تسجيل الأخطاء في المشاريع الحقيقية
        print(f"CRITICAL: Failed to award points to {student.username}. Error: {e}")