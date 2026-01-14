from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    last_mesocycle_start = models.DateField(null=True, blank=True)

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
    weight = models.FloatField(help_text="Вес в кг")
    reps = models.IntegerField(help_text="Количество повторений")
    estimated_1rm = models.FloatField(help_text="Расчётный 1RM (Epley)")
    updated_at = models.DateField(auto_now=True)
    notes = models.TextField(blank=True, max_length=500)

    class Meta:
        unique_together = ("user", "exercise")
        ordering = ["-updated_at"]

    def calculate_1rm_epley(self):
        """Epley formula: 1RM = weight * (1 + reps/30)"""
        if self.reps == 0:
            return self.weight
        return round(self.weight * (1 + self.reps / 30), 2)

    def calculate_1rm_brzycki(self):
        """Brzycki formula: 1RM = weight / (1.0278 - 0.0278 * reps)"""
        if self.reps == 0:
            return self.weight
        denominator = 1.0278 - 0.0278 * self.reps
        if denominator <= 0:
            return self.weight
        return round(self.weight / denominator, 2)

    def save(self, *args, **kwargs):
        self.estimated_1rm = self.calculate_1rm_epley()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.exercise.name}: {self.weight}kg x {self.reps}"


class Mesocycle(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="mesocycles")
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    start_date = models.DateField()
    week = models.IntegerField(
        choices=[(1, "Week 1"), (2, "Week 2"), (3, "Week 3"), (4, "Week 4")]
    )
    rpe = models.IntegerField(help_text="RPE (Rate of Perceived Exertion) 1-10")
    rir = models.IntegerField(help_text="RIR (Reps In Reserve)")
    target_weight = models.FloatField(help_text="Расчётный рабочий вес (кг)")
    target_reps_min = models.IntegerField()
    target_reps_max = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["start_date", "week"]
        unique_together = ("user", "exercise", "start_date", "week")

    def __str__(self):
        return f"{self.user.username} - {self.exercise.name} - Week {self.week}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()
