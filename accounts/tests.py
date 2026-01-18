from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from core.models import BestSet, BestSetHistory, Exercise, UserProfile


class BestSetModelTest(TestCase):
    def test_1rm_recalculated_on_save(self):
        user = User.objects.create_user(username="test")
        exercise = Exercise.objects.create(name="Squat")

        best_set = BestSet.objects.create(
            user=user, exercise=exercise, weight=120, reps=5
        )

        best_set.weight = 130
        best_set.reps = 3
        best_set.save()

        self.assertGreater(best_set.estimated_1rm, 120)


class BestSetHistoryTest(TestCase):
    def test_ordering_latest_first(self):
        user = User.objects.create_user(username="test")
        exercise = Exercise.objects.create(name="Deadlift")

        h1 = BestSetHistory.objects.create(
            user=user, exercise=exercise, weight=100, reps=5, estimated_1rm=120
        )
        h2 = BestSetHistory.objects.create(
            user=user, exercise=exercise, weight=110, reps=3, estimated_1rm=125
        )

        history = BestSetHistory.objects.all()
        self.assertEqual(history.first(), h2)


class UserProfileSignalTest(TestCase):
    def test_profile_created_on_user_creation(self):
        user = User.objects.create_user(username="signaltest")
        self.assertTrue(UserProfile.objects.filter(user=user).exists())


class AddBestSetViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test", password="123")
        self.exercise = Exercise.objects.create(name="Bench Press")

    def test_add_best_set(self):
        self.client.login(username="test", password="123")

        response = self.client.post(
            reverse("add_best_set"),
            {
                "exercise": self.exercise.id,
                "weight": 100,
                "reps": 5,
            },
        )

        self.assertEqual(BestSet.objects.count(), 1)
        self.assertRedirects(response, reverse("profile"))

    def test_worse_set_not_saved(self):
        BestSet.objects.create(
            user=self.user,
            exercise=self.exercise,
            weight=100,
            reps=5,
            estimated_1rm=120,
        )

        self.client.login(username="test", password="123")

        response = self.client.post(
            reverse("add_best_set"),
            {
                "exercise": self.exercise.id,
                "weight": 90,
                "reps": 5,
            },
        )

        best_set = BestSet.objects.get(user=self.user, exercise=self.exercise)
        self.assertEqual(best_set.weight, 100)


class Progress1RMTest(TestCase):
    def test_progress_data_exists(self):
        user = User.objects.create_user(username="test", password="123")
        exercise = Exercise.objects.create(name="Deadlift")

        BestSetHistory.objects.create(
            user=user,
            exercise=exercise,
            weight=150,
            reps=5,
            estimated_1rm=180,
        )

        self.client.login(username="test", password="123")
        response = self.client.get(reverse("progress_1rm"))

        self.assertContains(response, "Deadlift")
