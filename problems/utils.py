# gamification/utils.py

from django.db import transaction, F

def award_points(student, points):
    """
    3. CRITICAL FIX: The centralized, safe, and atomic point-awarding function.
    """
    if not student or not points or points <= 0:
        return

    try:
        with transaction.atomic():
            # Lock the row for the update to prevent race conditions
            user_to_update = student.__class__.objects.select_for_update().get(pk=student.pk)
            
            # Use F() expression to perform an atomic update at the database level
            user_to_update.score = F('score') + points
            user_to_update.save(update_fields=['score'])
            
            print(f"Awarded {points} points to {student.username}. New score will be calculated by DB.")

    except Exception as e:
        print(f"Error awarding points to {student.username}: {e}")