from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from core.models import BestSet, Exercise, Mesocycle

from .forms import BestSetForm, UserRegisterForm


def register(request):
    """User registration"""
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            messages.success(
                request, f"Account created for {username}! You can now log in."
            )
            return redirect("login")
    else:
        form = UserRegisterForm()

    return render(request, "accounts/register.html", {"form": form})


@login_required
def profile(request):
    """User profile with best sets and statistics"""
    user_best_sets = BestSet.objects.filter(user=request.user).select_related(
        "exercise"
    )

    context = {
        "best_sets": user_best_sets,
        "total_best_sets": user_best_sets.count(),
    }
    return render(request, "accounts/profile.html", context)


@login_required
def add_best_set(request):
    """Add/update best set"""
    exercise_id = request.GET.get("exercise")
    initial_exercise = None
    if exercise_id:
        try:
            initial_exercise = Exercise.objects.get(id=exercise_id)
        except Exercise.DoesNotExist:
            pass

    if request.method == "POST":
        form = BestSetForm(request.POST)
        if form.is_valid():
            new_weight = form.cleaned_data["weight"]
            new_reps = form.cleaned_data["reps"]
            new_exercise = form.cleaned_data["exercise"]

            new_1rm = round(new_weight * (1 + new_reps / 30), 2)

            existing_set = BestSet.objects.filter(
                user=request.user, exercise=new_exercise
            ).first()

            if existing_set:
                existing_1rm = existing_set.estimated_1rm

                if new_1rm < existing_1rm:
                    messages.warning(
                        request,
                        f"New set for '{new_exercise.name}' is worse than current "
                        f"(new 1RM: {new_1rm}kg < current: {existing_1rm}kg). "
                        f"Set not updated.",
                    )
                    return render(request, "accounts/add_best_set.html", {"form": form})

            best_set = form.save(commit=False)
            best_set.user = request.user

            if existing_set:
                best_set.pk = existing_set.pk
                messages.info(
                    request,
                    f"Set for '{new_exercise.name}' updated! 1RM: {new_1rm} kg",
                )
            else:
                messages.success(
                    request,
                    f"Set for '{new_exercise.name}' added! 1RM: {new_1rm} kg",
                )

            best_set.save()
            return redirect("profile")
    else:
        form = BestSetForm(initial={"exercise": initial_exercise})

    return render(request, "accounts/add_best_set.html", {"form": form})


@login_required
def delete_best_set(request, best_set_id):
    """Delete best set"""
    best_set = BestSet.objects.get(id=best_set_id, user=request.user)
    exercise_name = best_set.exercise.name
    best_set.delete()
    messages.success(request, f"Set for {exercise_name} deleted")
    return redirect("profile")


@login_required
def mesocycle(request):
    """
    Generate and display a 4-week mesocycle for main lifts
    """

    MAIN_EXERCISES = [
        "Barbell Back Squat",
        "Barbell Bench Press",
        "Deadlift",
    ]

    main_exercises = Exercise.objects.filter(name__in=MAIN_EXERCISES)

    user_best_set_ids = set(
        BestSet.objects.filter(user=request.user).values_list("exercise_id", flat=True)
    )

    missing_best_sets = [
        exercise.name
        for exercise in main_exercises
        if exercise.id not in user_best_set_ids
    ]

    mesocycles_by_exercise: dict[str, list[Mesocycle]] = {}
    start_date_display = None
    mesocycle_end_date = None

    if request.method == "POST" and not missing_best_sets:
        start_date_str = request.POST.get("start_date")

        if start_date_str:
            start_date = timezone.datetime.strptime(start_date_str, "%Y-%m-%d").date()

            Mesocycle.objects.filter(user=request.user, start_date=start_date).delete()

            weeks_config = [
                {"week": 1, "rpe": 7, "rir": 3, "mult": 0.85, "reps": (8, 12)},
                {"week": 2, "rpe": 8, "rir": 2, "mult": 0.90, "reps": (6, 10)},
                {"week": 3, "rpe": 10, "rir": 0, "mult": 0.95, "reps": (4, 8)},
                {"week": 4, "rpe": 5, "rir": 5, "mult": 0.70, "reps": (10, 15)},
            ]

            created_count = 0

            for exercise in main_exercises:
                best_set = BestSet.objects.get(user=request.user, exercise=exercise)

                base_1rm = best_set.estimated_1rm
                cycles = []

                for config in weeks_config:
                    cycle = Mesocycle.objects.create(
                        user=request.user,
                        exercise=exercise,
                        start_date=start_date,
                        week=config["week"],
                        rpe=config["rpe"],
                        rir=config["rir"],
                        target_weight=round(base_1rm * config["mult"], 1),
                        target_reps_min=config["reps"][0],
                        target_reps_max=config["reps"][1],
                    )
                    cycles.append(cycle)
                    created_count += 1

                mesocycles_by_exercise[exercise.name] = cycles

            start_date_display = start_date
            mesocycle_end_date = start_date + timedelta(days=27)

            messages.success(
                request,
                f"Mesocycle generated: "
                f"{start_date.strftime('%Y-%m-%d')} – "
                f"{mesocycle_end_date.strftime('%Y-%m-%d')} "
                f"({created_count} entries)",
            )

    if not mesocycles_by_exercise:
        latest_cycle = (
            Mesocycle.objects.filter(user=request.user)
            .order_by("-created_at")
            .select_related("exercise")
            .first()
        )

        if latest_cycle:
            start_date_display = latest_cycle.start_date
            mesocycle_end_date = start_date_display + timedelta(days=27)

            all_cycles = (
                Mesocycle.objects.filter(
                    user=request.user, start_date=start_date_display
                )
                .select_related("exercise")
                .order_by("exercise__name", "week")
            )

            for cycle in all_cycles:
                mesocycles_by_exercise.setdefault(cycle.exercise.name, []).append(cycle)

    for cycles in mesocycles_by_exercise.values():
        for cycle in cycles:
            week_start = cycle.start_date + timedelta(days=(cycle.week - 1) * 7)
            week_end = week_start + timedelta(days=6)

            cycle.week_start = week_start
            cycle.week_end = week_end

    context = {
        "main_exercises": main_exercises,
        "missing_best_sets": missing_best_sets,
        "mesocycles_by_exercise": mesocycles_by_exercise,
        "mesocycle_exists": bool(mesocycles_by_exercise),
        "today": timezone.now().date(),
        "start_date": start_date_display,
        "mesocycle_end_date": mesocycle_end_date,
    }

    return render(request, "accounts/mesocycle.html", context)
