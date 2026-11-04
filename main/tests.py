from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from main.models import Experience, Education


class MainTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Asisten Dosen PBP",
            description="Membantu mahasiswa memahami pengembangan web.",
            category="part-time",
        )

    def test_main_url_is_accessible(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertNotContains(response, self.experience.title)
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/halaman-yang-tidak-ada/")

        self.assertEqual(response.status_code, 404)

    def test_experience_model(self):
        self.assertEqual(str(self.experience), "Asisten Dosen PBP")
        self.assertEqual(self.experience.category, "part-time")
        self.assertTrue(self.experience.is_ongoing)

    def test_experience_page(self):
        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertContains(response, self.experience.title)
        self.assertContains(response, self.experience.description)
        self.assertContains(response, "Part-Time")
        self.assertContains(response, "Sedang berlangsung")
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

    def test_empty_experience_page(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:show_experience"))

        self.assertContains(response, "Belum ada pengalaman yang ditambahkan.")

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        response = self.client.get(reverse("main:show_experience"))

        self.assertFalse(self.experience.is_ongoing)
        self.assertContains(response, "Selesai")
        self.assertNotContains(response, "Sedang berlangsung")

class EducationTest(TestCase):
    def test_education_url_and_template(self):
        response = self.client.get(reverse("main:show_education"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "education.html")

    def test_education_page_displays_all_data(self):
        university = Education.objects.create(
            title="Universitas Contoh",
            description="Menempuh pendidikan S1 Sistem Informasi.",
            category="university",
        )
        school = Education.objects.create(
            title="SMA Contoh",
            description="Menempuh pendidikan menengah atas.",
            category="senior high school",
        )

        page = self.client.get(reverse("main:show_education"))
        self.assertContains(page, 'id="education-grid"')
        self.assertContains(page, reverse("main:get_education_json"))
        self.assertContains(page, 'js/education.js')

        response = self.client.get(reverse("main:get_education_json"))
        self.assertEqual(response.status_code, 200)
        records = {item["pk"]: item["fields"] for item in response.json()}
        self.assertEqual(len(records), 2)
        for education in (university, school):
            with self.subTest(title=education.title):
                record = records[str(education.pk)]
                self.assertEqual(record["title"], education.title)
                self.assertEqual(record["description"], education.description)
                self.assertEqual(record["category_display"], education.get_category_display())

    def test_empty_education_page(self):
        page = self.client.get(reverse("main:show_education"))
        self.assertContains(page, 'id="education-empty"')
        self.assertContains(page, 'id="education-empty-message"')
        response = self.client.get(reverse("main:get_education_json"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])
