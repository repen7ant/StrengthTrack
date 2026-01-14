from django.core.management.base import BaseCommand

from core.models import Exercise


class Command(BaseCommand):
    help = "Заполняет базу упражнениями"

    def handle(self, *args, **options):
        exercises = [
            "Barbell Back Squat",
            "Barbell Bench Press",
            "Incline Barbell Bench Press",
            "Deadlift",
            "Romanian Deadlift",
            "Overhead Barbell Press",
            "Seated Dumbbell Shoulder Press",
            "Dumbbell Lateral Raises",
            "Cable Lateral Raises",
            "Weighted Pull-Ups",
            "Bent-Over Barbell Row",
            "Seated Cable Row",
            "Lat Pulldown",
            "Barbell Hip Thrust",
            "Leg Press",
            "Standing Calf Raises",
            "Seated Calf Raises",
            "Dumbbell Bench Press",
            "Incline Dumbbell Bench Press",
            "Dumbbell Flyes",
            "Weighted Dips",
            "Barbell Curl",
            "Dumbbell Curl",
            "Incline Bench Dumbbell Curl",
            "Hammer Curl",
            "Skull Crushers",
            "Cable Triceps Pushdown",
            "Leg Extension",
            "Leg Curl",
        ]

        created_count = 0
        for name in exercises:
            exercise, created = Exercise.objects.get_or_create(name=name)
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Создано: {exercise.name}"))
            else:
                self.stdout.write(
                    self.style.WARNING(f"Уже существует: {exercise.name}")
                )

        self.stdout.write(
            self.style.SUCCESS(f"Готово! Создано {created_count} новых упражнений.")
        )
