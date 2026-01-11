from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import UserRegisterForm, UserUpdateForm


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
    """Профиль пользователя"""
    if request.method == "POST":
        user_form = UserUpdateForm(request.POST, instance=request.user)

        if user_form.is_valid():
            user_form.save()
            messages.success(request, "Ваш профиль был обновлен!")
            return redirect("profile")
    else:
        user_form = UserUpdateForm(instance=request.user)

    context = {
        "user_form": user_form,
    }
    return render(request, "accounts/profile.html", context)
