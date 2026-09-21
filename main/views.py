from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from main.forms import EducationForm, ProjectForm
from main.models import Education, Experience, Project


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
        "name": "Rayyan Raditia Pramana",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)


def show_education(request):
    context = {
        "name": "Rayyan Raditia Pramana",
        "education_list": Education.objects.all(),
    }
    return render(request, "education.html", context)


def create_project(request):
    form = ProjectForm(
        request.POST if request.method == "POST" else None
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proyek baru berhasil ditambahkan!")
        return redirect("main:show_projects")

    context = {
        "name": "Rayyan Raditia Pramana",
        "form": form,
    }
    return render(request, "projects_form.html", context)


def get_projects_json(request):
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.all()

    if title_query:
        projects = projects.filter(title__icontains=title_query)

    projects_json = serializers.serialize("json", projects)
    return HttpResponse(
        projects_json,
        content_type="application/json",
    )


def show_projects(request):
    json_response = get_projects_json(request)

    projects = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )

    context = {
        "name": "Rayyan Raditia Pramana",
        "project_list": [project.object for project in projects],
        "title_query": request.GET.get("title", "").strip(),
    }
    return render(request, "project.html", context)


def delete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        project.delete()
        messages.success(request, "Proyek berhasil dihapus!")

    return redirect("main:show_projects")

def create_education(request):
    form = EducationForm(
        request.POST if request.method == "POST" else None
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Pendidikan berhasil ditambahkan!")
        return redirect("main:show_education")

    context = {
        "name": "Rayyan Raditia Pramana",
        "form": form,
        "page_title": "Tambah Pendidikan",
        "submit_label": "Tambah Pendidikan",
    }
    return render(request, "education_form.html", context)


def update_education(request, education_id):
    education = get_object_or_404(Education, pk=education_id)

    form = EducationForm(
        request.POST if request.method == "POST" else None,
        instance=education,
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Pendidikan berhasil diperbarui!")
        return redirect("main:show_education")

    context = {
        "name": "Rayyan Raditia Pramana",
        "form": form,
        "page_title": "Edit Pendidikan",
        "submit_label": "Simpan Perubahan",
    }
    return render(request, "education_form.html", context)


@require_POST
def delete_education(request, education_id):
    education = get_object_or_404(Education, pk=education_id)
    education.delete()

    messages.success(request, "Pendidikan berhasil dihapus!")
    return redirect("main:show_education")


def get_education_json(request):
    education_list = Education.objects.all()
    education_json = serializers.serialize("json", education_list)

    return HttpResponse(
        education_json,
        content_type="application/json",
    )