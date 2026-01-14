from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from core.models import BestSet, Exercise

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
