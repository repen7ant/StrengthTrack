from django.shortcuts import render


def home(request):
    """Main page"""
    return render(request, "core/home.html")
