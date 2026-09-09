from django.shortcuts import render

from main.models import Experience


def show_main(request):
    context = {
        "name": "Rayyan Raditia Pramana",
        "npm": "2506598955",
        "study_program": "S1 Sistem Informasi",
        "bio": (
            "Information Systems student with a strong interest in the intersection of management, finance, technology, and "
            "data science. Highly adaptable and eager to learn new skills, with a passion for continuous growth. Enthusiastic about "
            "contributing to team success and collaborating to achieve shared goals."
        ),
    }
    return render(request, "index.html", context)


def show_experience(request):
    context = {
        "name": "Rayyan",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)