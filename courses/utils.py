# gamification/utils.py

from django.db import transaction, F

def award_points(student, points):
    """
    Safely awards points to a student.
    - Uses a transaction to ensure atomicity.
    - Uses F() expressions to prevent race conditions.
    """
    if not student or not points or points <= 0:
        return

    try:
        # 4. CRITICAL FIX (Atomicity): Ensures that the entire operation succeeds or fails together.
        with transaction.atomic():
            # The `select_for_update()` locks the user row, preventing other processes
            # from modifying it until this transaction is complete.
            user_to_update = student.__class__.objects.select_for_update().get(pk=student.pk)
            
            # 5. CRITICAL FIX (Race Condition): F() expressions update the value directly in the database.
            # This is an atomic operation and avoids the read-then-write problem.
            user_to_update.score = F('score') + points
            user_to_update.save(update_fields=['score'])

    except Exception as e:
        # Handle potential exceptions, e.g., log the error
        print(f"Error awarding points to {student.username}: {e}")