from django.shortcuts import render


def home(request):
    """Главная страница"""
    context = {
        "title": "StrengthTrack - Система планирования тренировок",
        "features": [
            "Планирование тренировок по принципам RIR/RPE",
            "Автоматическая генерация мезоциклов",
            "Отслеживание прогресса",
            "Визуализация результатов",
        ],
    }
    return render(request, "core/home.html", context)
