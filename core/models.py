from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} Profile"


class Exercise(models.Model):
    name = models.CharField(max_length=200, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Упражнение"
        verbose_name_plural = "Упражнения"

    def __str__(self):
        return self.name


class BestSet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="best_sets")
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    weight = models.FloatField(help_text="Weight in kg")
    reps = models.IntegerField(help_text="Repetitions")
    estimated_1rm = models.FloatField(help_text="Calculated 1RM (Brzycki)")
    updated_at = models.DateField(auto_now=True)

    def calculate_1rm_brzycki(self):
        """Brzycki formula: 1RM = weight / (1.0278 - 0.0278 * reps)"""
        if self.reps == 0:
            return self.weight
        denominator = 1.0278 - 0.0278 * self.reps
        if denominator <= 0:
            return self.weight
        return round(self.weight / denominator, 2)

    def save(self, *args, **kwargs):
        self.estimated_1rm = self.calculate_1rm_brzycki()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.exercise.name}: {self.weight}kg x {self.reps} (1RM: {self.estimated_1rm}kg)"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()


class Mesocycle(models.Model):
    MAIN_EXERCISES = ["Barbell Back Squat", "Barbell Bench Press", "Deadlift"]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="mesocycles")
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    start_date = models.DateField()
    week = models.IntegerField(
        choices=[(1, "Week 1"), (2, "Week 2"), (3, "Week 3"), (4, "Week 4")]
    )
    rpe = models.IntegerField()
    rir = models.IntegerField()
    target_weight = models.FloatField()
    target_reps_min = models.IntegerField()
    target_reps_max = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.exercise.name} - Week {self.week}"


class BestSetHistory(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="best_set_history"
    )
    exercise = models.ForeignKey(
        Exercise, on_delete=models.CASCADE, related_name="best_set_history"
    )

    weight = models.FloatField(help_text="Weight in kg")
    reps = models.IntegerField(help_text="Repetitions")
    estimated_1rm = models.FloatField(help_text="Calculated 1RM (Brzycki)")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"{self.user.username} - {self.exercise.name}: "
            f"{self.weight}kg x {self.reps} ({self.estimated_1rm}kg)"
        )
