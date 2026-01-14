from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import BestSet, Exercise, Mesocycle, UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False


class CustomUserAdmin(UserAdmin):
    inlines = [UserProfileInline]
    list_display = [
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "date_joined",
    ]
    list_filter = ["is_staff", "is_superuser", "is_active"]
    search_fields = ["username", "email", "first_name", "last_name"]


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")  # Только название и дата создания
    list_display_links = ("name",)  # Клик по названию = редактирование
    search_fields = ("name",)  # Поиск по названию
    list_per_page = 50  # 50 на страницу
    fields = ("name",)  # Только поле name в форме
    readonly_fields = ("created_at",)  # Дата создания только для чтения

    def has_add_permission(self, request):
        """Разрешить добавление только через админку"""
        return True


@admin.register(BestSet)
class BestSetAdmin(admin.ModelAdmin):
    list_display = ("exercise", "user", "weight", "reps", "estimated_1rm", "updated_at")
    list_filter = ("exercise", "updated_at")
    search_fields = ("exercise__name", "user__username")
    readonly_fields = ("estimated_1rm", "updated_at")


admin.site.register(UserProfile)
admin.site.register(Mesocycle)
