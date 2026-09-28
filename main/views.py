from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import redirect, render
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from main.forms import EducationForm, ProjectForm
from main.models import Education, Experience, Project

import datetime
from django.contrib.auth.decorators import login_required  
from django.core.exceptions import PermissionDenied        


def show_main(request):
    last_login = request.COOKIES.get('last_login', 'Belum ada sesi login / Cookie tidak ditemukan')
    context = {
        "name": "Rayyan Raditia Pramana",
        "npm": "2506598955",
        "study_program": "S1 Sistem Informasi",
        "bio": (
            "Information Systems student with a strong interest in the intersection of management, finance, technology, and "
            "data science. Highly adaptable and eager to learn new skills, with a passion for continuous growth. Enthusiastic about "
            "contributing to team success and collaborating to achieve shared goals."
        ),
        "last_login": last_login,
    }
    return render(request, "index.html", context)


def show_experience(request):
    context = {
        "name": "Rayyan Raditia Pramana",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)


def show_education(request):
    json_response = get_education_json(request)

    education_objects = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )

    context = {
        "name": "Rayyan Raditia Pramana",
        "education_list": [
            education.object for education in education_objects
        ],
    }
    return render(request, "education.html", context)


@login_required(login_url="/login/")
def create_project(request):
    if not request.user.is_superuser:
        raise PermissionDenied
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

    projects_json = serializers.serialize("json", projects, use_natural_foreign_keys=True)
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


@login_required(login_url="/login/")
def delete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if not request.user.is_superuser:
        raise PermissionDenied

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

def register(request):
    form = UserCreationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Akun berhasil dibuat. Silakan login.")
        return redirect("main:login")

    context = {
        "name": "Rayyan Raditia Pramana",
        "form": form,
    }
    return render(request, "register.html", context)

def login_user(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        response = redirect("main:show_main")
        response.set_cookie('last_login', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        return response

    context = {
        "name": "Rayyan Raditia Pramana",
        "form": form,
    }
    return render(request, "login.html", context)

def logout_user(request):
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie('last_login')
    return response

@login_required(login_url="/login/")
def toggle_star(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        # Kalau akun ini sudah pernah memberi star, batalkan star-nya.
        # Kalau belum, tambahkan star.
        if request.user in project.starred_by.all():
            project.starred_by.remove(request.user)
        else:
            project.starred_by.add(request.user)

    return redirect("main:show_projects")
