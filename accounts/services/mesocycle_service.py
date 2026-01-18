from datetime import timedelta
from typing import Dict, List

from django.db import transaction
from django.utils import timezone

from core.models import BestSet, Exercise, Mesocycle

MAIN_EXERCISES_NAMES = [
    "Barbell Back Squat",
    "Barbell Bench Press",
    "Deadlift",
]


class MesocycleService:
    """Handles mesocycle generation and retrieval."""

    WEEKS_CONFIG = [
        {"week": 1, "rpe": 7, "rir": 3, "mult": 0.75, "reps": (8, 12)},
        {"week": 2, "rpe": 8, "rir": 2, "mult": 0.80, "reps": (6, 10)},
        {"week": 3, "rpe": 10, "rir": 0, "mult": 0.9, "reps": (4, 7)},
        {"week": 4, "rpe": 5, "rir": 5, "mult": 0.60, "reps": (10, 15)},
    ]

    @staticmethod
    def get_main_exercises() -> List[Exercise]:
        """Get main exercises."""
        return list(Exercise.objects.filter(name__in=MAIN_EXERCISES_NAMES))

    @staticmethod
    def check_missing_best_sets(user, main_exercises: List[Exercise]) -> List[str]:
        """Check which main exercises lack best sets."""
        user_best_set_ids = set(
            BestSet.objects.filter(user=user).values_list("exercise_id", flat=True)
        )
        return [
            exercise.name
            for exercise in main_exercises
            if exercise.id not in user_best_set_ids
        ]

    @staticmethod
    @transaction.atomic
    def generate_mesocycle(user, start_date_str: str) -> tuple:
        """Generate 4-week mesocycle, returns (start_date, end_date, created_count, success)."""
        start_date = timezone.datetime.strptime(start_date_str, "%Y-%m-%d").date()

        Mesocycle.objects.filter(user=user, start_date=start_date).delete()

        main_exercises = MesocycleService.get_main_exercises()

        created_count = 0
        mesocycles_by_exercise = {}

        for exercise in main_exercises:
            best_set = BestSet.objects.get(user=user, exercise=exercise)
            base_1rm = best_set.estimated_1rm
            cycles = []

            for config in MesocycleService.WEEKS_CONFIG:
                raw_weight = base_1rm * config["mult"]
                target_weight = round_to_plates(raw_weight)

                cycle = Mesocycle.objects.create(
                    user=user,
                    exercise=exercise,
                    start_date=start_date,
                    week=config["week"],
                    rpe=config["rpe"],
                    rir=config["rir"],
                    target_weight=target_weight,
                    target_reps_min=config["reps"][0],
                    target_reps_max=config["reps"][1],
                )
                cycles.append(cycle)
                created_count += 1

            mesocycles_by_exercise[exercise.name] = cycles

        end_date = start_date + timedelta(days=27)
        return start_date, end_date, created_count, True

    @staticmethod
    def get_latest_mesocycles(user) -> Dict[str, List[Mesocycle]]:
        """Get latest mesocycles grouped by exercise."""
        latest_cycle = (
            Mesocycle.objects.filter(user=user)
            .order_by("-created_at")
            .select_related("exercise")
            .first()
        )
        if not latest_cycle:
            return {}

        start_date = latest_cycle.start_date
        all_cycles = (
            Mesocycle.objects.filter(user=user, start_date=start_date)
            .select_related("exercise")
            .order_by("exercise__name", "week")
        )

        mesocycles_by_exercise = {}
        for cycle in all_cycles:
            mesocycles_by_exercise.setdefault(cycle.exercise.name, []).append(cycle)

        return mesocycles_by_exercise

    @staticmethod
    def add_week_dates(mesocycles_by_exercise: Dict[str, List[Mesocycle]]):
        """Add computed week start/end dates to cycles."""
        for cycles in mesocycles_by_exercise.values():
            for cycle in cycles:
                week_start = cycle.start_date + timedelta(days=(cycle.week - 1) * 7)
                week_end = week_start + timedelta(days=6)
                cycle.week_start = week_start
                cycle.week_end = week_end


def round_to_plates(weight: float, plate_size: float = 1.25) -> float:
    """
    Round weight to the nearest achievable value using plates.
    Default: 1.25 kg plates (2.5 kg total step).
    """
    step = plate_size * 2
    return round(weight / step) * step
