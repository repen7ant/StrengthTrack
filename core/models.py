from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    profile_image = models.ImageField(upload_to="profile_images/", blank=True)

    # Тренировочные данные
    training_experience = models.IntegerField(
        default=0, help_text="Опыт тренировок (в месяцах)"
    )
    primary_goal = models.CharField(
        max_length=100,
        blank=True,
        choices=[
            ("strength", "Сила"),
            ("hypertrophy", "Мышечная масса"),
            ("endurance", "Выносливость"),
        ],
    )

    def __str__(self):
        return f"{self.user.username} Profile"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

