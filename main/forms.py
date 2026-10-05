from django.forms import ModelForm, TextInput, Textarea, URLInput

from main.models import Education, Project
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags

class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = [
            "title",
            "description",
            "tech_stack",
            "project_url",
            "project_image_url",
        ]

        labels = {
            "title": "Nama Proyek",
            "description": "Deskripsi Proyek",
            "tech_stack": "Teknologi yang Digunakan",
            "project_url": "URL Proyek",
            "project_image_url": "URL Gambar Proyek",
        }

        widgets = {
            "title": TextInput(
                attrs={
                    "placeholder": "Portfolio Website",
                    "maxlength": 255,
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Ceritakan Proyekmu",
                    "rows": 3,
                }
            ),
            "tech_stack": TextInput(
                attrs={
                    "placeholder": "Django, Python, HTML, CSS",
                }
            ),
            "project_url": URLInput(
                attrs={
                    "placeholder": "https://github.com/kakBurhan/burhanquestv4",
                }
            ),
            "project_image_url": URLInput(
                attrs={
                    "placeholder": "https://drive.google.com/thumbnail?id=...&sz=w1000",
                }
            ),
        }
    def clean_title(self):
        title = strip_tags(self.cleaned_data["title"]).strip()
        if not title:
            raise ValidationError("Nama proyek tidak boleh hanya berisi tag HTML.")
        return title

    def clean_tech_stack(self):
        return strip_tags(self.cleaned_data["tech_stack"]).strip()

    def clean_description(self):
        return strip_tags(self.cleaned_data["description"]).strip()

class EducationForm(ModelForm):
    class Meta:
        model = Education

        fields = [
            "title",
            "description",
            "category",
            "thumbnail",
        ]

        labels = {
            "title": "Nama Institusi",
            "description": "Deskripsi Pendidikan",
            "category": "Jenjang Pendidikan",
            "thumbnail": "URL Logo Institusi",
        }

        widgets = {
            "title": TextInput(
                attrs={
                    "placeholder": "Universitas Indonesia",
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Ceritakan pendidikanmu",
                    "rows": 3,
                }
            ),
            "thumbnail": URLInput(
                attrs={
                    "placeholder": "https://example.com/logo.png",
                }
            ),
        }

    def clean_title(self):
        title = strip_tags(self.cleaned_data["title"]).strip()

        if not title:
            raise ValidationError(
                "Nama institusi tidak boleh kosong atau hanya berisi tag HTML."
            )

        return title

    def clean_description(self):
        description = strip_tags(
            self.cleaned_data["description"]
        ).strip()

        if not description:
            raise ValidationError(
                "Deskripsi pendidikan tidak boleh kosong atau hanya berisi tag HTML."
            )

        return description
