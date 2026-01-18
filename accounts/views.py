from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from .forms import BestSetForm, UserRegisterForm
from .services import (
    BestSetService,
    MesocycleService,
    ProfileService,
    ProgressService,
)


def register(request):
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
    user_best_sets = ProfileService.get_user_best_sets(request.user)

    context = {
        "best_sets": user_best_sets,
        "total_best_sets": user_best_sets.count(),
    }
    return render(request, "accounts/profile.html", context)


@login_required
def add_best_set(request):
    exercise_id = request.GET.get("exercise")
    initial_exercise = BestSetService.get_initial_exercise(exercise_id)

    if request.method == "POST":
        form = BestSetForm(request.POST)
        if form.is_valid():
            success, message = BestSetService.add_or_update_best_set(
                request.user, form.cleaned_data
            )
            if success:
                messages.success(request, message)
                return redirect("profile")
            else:
                messages.warning(request, message)
                return render(request, "accounts/add_best_set.html", {"form": form})
    else:
        form = BestSetForm(initial={"exercise": initial_exercise})

    return render(request, "accounts/add_best_set.html", {"form": form})


@login_required
def delete_best_set(request, best_set_id):
    message = BestSetService.delete_best_set(request.user, best_set_id)
    messages.success(request, message)
    return redirect("profile")


@login_required
def mesocycle(request):
    main_exercises = MesocycleService.get_main_exercises()
    missing_best_sets = MesocycleService.check_missing_best_sets(
        request.user, main_exercises
    )

    mesocycles_by_exercise = {}
    start_date_display = None
    mesocycle_end_date = None

    if request.method == "POST" and not missing_best_sets:
        start_date_str = request.POST.get("start_date")
        if start_date_str:
            start_date, end_date, created_count, success = (
                MesocycleService.generate_mesocycle(request.user, start_date_str)
            )
            if success:
                messages.success(
                    request,
                    f"Mesocycle generated: "
                    f"{start_date.strftime('%Y-%m-%d')} – "
                    f"{end_date.strftime('%Y-%m-%d')} "
                    f"({created_count} entries)",
                )

    mesocycles_by_exercise = MesocycleService.get_latest_mesocycles(request.user)

    if mesocycles_by_exercise:
        start_date_display = next(iter(mesocycles_by_exercise.values()))[0].start_date
        mesocycle_end_date = start_date_display + timedelta(days=27)

    MesocycleService.add_week_dates(mesocycles_by_exercise)

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


@login_required
def progress_1rm(request):
    charts_data = ProgressService.get_progress_charts_data(request.user)

    context = {"charts_data": charts_data}
    return render(request, "accounts/progress_1rm.html", context)
