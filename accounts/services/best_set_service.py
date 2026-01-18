from typing import Optional

from django.db import transaction
from django.utils import timezone

from core.models import BestSet, BestSetHistory, Exercise


class BestSetService:
    """Handles all best set operations: add, update, delete."""

    @staticmethod
    @transaction.atomic
    def add_or_update_best_set(user, form_data: dict) -> tuple[bool, Optional[str]]:
        """Add or update best set, returns (success, message)."""
        weight = form_data["weight"]
        reps = form_data["reps"]
        exercise = form_data["exercise"]

        new_1rm = round(weight / (1.0278 - 0.0278 * reps), 2)

        existing_set = BestSet.objects.filter(user=user, exercise=exercise).first()

        if existing_set:
            existing_1rm = existing_set.estimated_1rm
            if new_1rm < existing_1rm:
                return (
                    False,
                    f"New set for '{exercise.name}' is worse than current (new 1RM: {new_1rm}kg < current: {existing_1rm}kg). Set not updated.",
                )

            BestSetHistory.objects.create(
                user=user,
                exercise=existing_set.exercise,
                weight=existing_set.weight,
                reps=existing_set.reps,
                estimated_1rm=existing_set.estimated_1rm,
            )

            existing_set.weight = weight
            existing_set.reps = reps
            existing_set.estimated_1rm = new_1rm
            existing_set.updated_at = timezone.now()
            existing_set.save()
            return True, f"Set for '{exercise.name}' updated! 1RM: {new_1rm} kg"

        BestSet.objects.create(
            user=user,
            exercise=exercise,
            weight=weight,
            reps=reps,
            estimated_1rm=new_1rm,
        )
        return True, f"Set for '{exercise.name}' added! 1RM: {new_1rm} kg"

    @staticmethod
    def delete_best_set(user, best_set_id: int) -> str:
        """Delete best set and its history."""
        best_set = BestSet.objects.get(id=best_set_id, user=user)
        exercise = best_set.exercise

        BestSetHistory.objects.filter(user=user, exercise=exercise).delete()
        best_set.delete()

        return f"Set and history for {exercise.name} deleted"

    @staticmethod
    def get_initial_exercise(exercise_id: str) -> Optional[Exercise]:
        """Get exercise for initial form data."""
        if not exercise_id:
            return None
        try:
            return Exercise.objects.get(id=exercise_id)
        except Exercise.DoesNotExist:
            return None
