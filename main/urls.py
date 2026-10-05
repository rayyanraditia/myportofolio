from django.urls import path

from main.views import (
    create_education,
    create_project,
    delete_education,
    delete_project,
    get_education_json,
    get_projects_json,
    show_education,
    show_experience,
    show_main,
    show_projects,
    update_education,
    register,
    login_user,
    logout_user,
    toggle_star,
    toggle_education_star,
    create_project_ajax,
    create_education_ajax,
)

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),
    path("education/", show_education, name="show_education"),
    path("projects/", show_projects, name="show_projects"),
    path("projects/add/", create_project, name="create_project"),
    path("api/projects/", get_projects_json, name="get_projects_json",),
    path("projects/<uuid:project_id>/delete/", delete_project, name="delete_project",),
    path("education/add/", create_education, name="create_education",),
    path("education/<uuid:education_id>/edit/", update_education, name="update_education",),
    path("education/<uuid:education_id>/delete/", delete_education, name="delete_education",),
    path("api/education/", get_education_json,name="get_education_json",),
    path("register/", register, name="register"),
    path("login/", login_user, name="login"),
    path("logout/", logout_user, name="logout"),
    path("projects/<uuid:project_id>/star/", toggle_star, name="toggle_star",),
    path("education/<uuid:education_id>/star/", toggle_education_star, name="toggle_education_star",),
    path("projects/add-ajax/", create_project_ajax, name="create_project_ajax"),
    path("education/add-ajax/", create_education_ajax, name="create_education_ajax",),
]
