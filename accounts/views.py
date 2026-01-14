from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from core.models import BestSet

from .forms import BestSetForm, UserRegisterForm


def register(request):
    """Регистрация нового пользователя"""
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            messages.success(
                request, f"Аккаунт создан для {username}! Теперь вы можете войти."
            )
            return redirect("login")
    else:
        form = UserRegisterForm()

    return render(request, "accounts/register.html", {"form": form})


@login_required
def profile(request):
    """Профиль пользователя с лучшими подходами и статистикой"""
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
    """Добавление/обновление лучшего подхода"""
    if request.method == "POST":
        form = BestSetForm(request.POST)
        if form.is_valid():
            best_set = form.save(commit=False)
            best_set.user = request.user

            # Проверка на уникальность (user, exercise)
            existing_set = BestSet.objects.filter(
                user=request.user, exercise=best_set.exercise
            ).first()

            if existing_set:
                best_set.pk = existing_set.pk
                messages.info(
                    request, f"Подход обновлён! Новый 1RM: {best_set.estimated_1rm} кг"
                )
            else:
                messages.success(
                    request,
                    f"Подход добавлен! Расчётный 1RM: {best_set.estimated_1rm} кг",
                )

            best_set.save()
            return redirect("profile")
    else:
        form = BestSetForm()

    return render(request, "accounts/add_best_set.html", {"form": form})


@login_required
def delete_best_set(request, best_set_id):
    """Удаление лучшего подхода"""
    best_set = BestSet.objects.get(id=best_set_id, user=request.user)
    exercise_name = best_set.exercise.name
    best_set.delete()
    messages.success(request, f"Подход для {exercise_name} удалён")
    return redirect("profile")
