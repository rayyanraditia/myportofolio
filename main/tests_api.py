import uuid

from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from main.models import Education, Project


class ProjectAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser('owner', 'owner@example.com', 'test-password')
        self.visitor = User.objects.create_user('visitor', password='test-password')
        self.project = Project.objects.create(
            title='Portfolio', description='My website', tech_stack='Django',
        )
        self.list_url = reverse('api:project-list')
        self.detail_url = reverse('api:project-detail', args=[self.project.pk])
        self.star_url = reverse('api:project-star', args=[self.project.pk])
        self.payload = {
            'title': 'New project', 'description': 'A useful app',
            'tech_stack': 'Python', 'project_url': 'https://example.com/',
            'project_image_url': '',
        }

    def test_public_list_and_detail(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]['id'], str(self.project.pk))
        self.assertFalse(response.data[0]['is_starred'])
        self.assertNotIn('fields', response.data[0])
        self.assertEqual(self.client.get(self.detail_url).status_code, 200)

    def test_search_and_empty_results(self):
        result = self.client.get(self.list_url, {'title': 'PORT'})
        self.assertEqual(result.status_code, 200)
        self.assertEqual(len(result.data), 1)
        result = self.client.get(self.list_url, {'title': 'not-found'})
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.data, [])

    def test_missing_project(self):
        url = reverse('api:project-detail', args=[uuid.uuid4()])
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_guest_and_visitor_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            with self.subTest(user=user):
                self.assertEqual(self.client.post(self.list_url, self.payload, format='json').status_code, 403)
                for method in ('put', 'patch', 'delete'):
                    response = getattr(self.client, method)(self.detail_url, self.payload, format='json')
                    self.assertEqual(response.status_code, 403)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, 'Portfolio')
        self.assertEqual(Project.objects.count(), 1)

    def test_owner_can_create(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, self.payload, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Project.objects.filter(pk=response.data['id']).exists())

    def test_validation(self):
        self.client.force_authenticate(user=self.owner)
        for changes, field in [
            ({'title': '   '}, 'title'),
            ({'title': '<img src="x" onerror="alert(1)">'}, 'title'),
            ({'project_url': 'javascript:alert(1)'}, 'project_url'),
        ]:
            with self.subTest(changes=changes):
                response = self.client.post(self.list_url, {**self.payload, **changes}, format='json')
                self.assertEqual(response.status_code, 400)
                self.assertIn(field, response.data)
        self.assertEqual(Project.objects.count(), 1)

    def test_patch_put_and_delete(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(self.detail_url, {'title': 'Changed'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, 'Changed')
        self.assertEqual(self.project.description, 'My website')
        self.assertEqual(self.client.put(self.detail_url, {'title': 'Incomplete'}, format='json').status_code, 400)
        self.assertEqual(self.client.put(self.detail_url, self.payload, format='json').status_code, 200)
        self.project.refresh_from_db()
        self.assertEqual(self.project.description, self.payload['description'])
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b'')
        self.assertFalse(Project.objects.filter(pk=self.project.pk).exists())

    def test_star_requires_login_and_toggles(self):
        self.assertEqual(self.client.post(self.star_url).status_code, 403)
        self.client.force_authenticate(user=self.visitor)
        response = self.client.post(self.star_url, {'user_id': self.owner.pk}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['is_starred'])
        self.assertEqual(response.data['star_count'], 1)
        self.assertTrue(self.project.starred_by.filter(pk=self.visitor.pk).exists())
        self.assertFalse(self.project.starred_by.filter(pk=self.owner.pk).exists())
        response = self.client.post(self.star_url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data['is_starred'])
        self.assertEqual(response.data['star_count'], 0)

    def test_computed_fields_are_read_only(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, {
            **self.payload, 'star_count': 99, 'is_starred': True,
            'starred_by_names': 'forged', 'starred_by': [self.visitor.pk],
        }, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['star_count'], 0)
        self.assertFalse(response.data['is_starred'])
        self.assertEqual(response.data['starred_by_names'], '')
        self.assertFalse(Project.objects.get(pk=response.data['id']).starred_by.exists())

    def test_staff_and_editor_cannot_manage_tutorial_projects(self):
        self.visitor.is_staff = True
        self.visitor.save()
        self.visitor.groups.add(Group.objects.create(name='Editor'))
        self.client.force_authenticate(user=self.visitor)
        self.assertEqual(self.client.patch(self.detail_url, {'title': 'Changed'}, format='json').status_code, 403)

    def test_wrong_method(self):
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(self.client.delete(self.list_url).status_code, 405)
        self.assertEqual(self.client.get(self.star_url).status_code, 405)

    def test_session_write_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username='owner', password='test-password'))
        response = client.post(self.list_url, self.payload, format='json')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Project.objects.count(), 1)

    def test_session_write_with_csrf_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username='owner', password='test-password'))
        page = client.get(self.list_url, HTTP_ACCEPT='text/html')
        self.assertEqual(page.status_code, 200)
        token = client.cookies['csrftoken'].value
        response = client.post(self.list_url, self.payload, format='json', HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 201)
        # Projects must also issue a token for a logged-in visitor's star request.
        client.logout()
        self.assertTrue(client.login(username='visitor', password='test-password'))
        client.cookies.pop('csrftoken', None)
        self.assertEqual(client.get(reverse('main:show_projects')).status_code, 200)
        token = client.cookies['csrftoken'].value
        response = client.post(self.star_url, HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['is_starred'])

class EducationAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="education_owner",
            email="owner@example.com",
            password="test-password",
        )
        self.visitor = User.objects.create_user(
            username="education_visitor",
            password="test-password",
        )
        self.editor = User.objects.create_user(
            username="education_editor",
            password="test-password",
        )
        editor_group = Group.objects.create(name="Editor")
        self.editor.groups.add(editor_group)

        self.education = Education.objects.create(
            title="Universitas Indonesia",
            description="S1 Sistem Informasi",
            category="university",
        )

        self.list_url = reverse("api:education-list")
        self.detail_url = reverse(
            "api:education-detail",
            args=[self.education.pk],
        )
        self.star_url = reverse(
            "api:education-star",
            args=[self.education.pk],
        )
        self.payload = {
            "title": "Institusi Baru",
            "description": "Deskripsi pendidikan baru",
            "category": "university",
            "thumbnail": "",
        }

    def database_snapshot(self):
        """Capture records and stars to detect unauthorized changes."""
        records = list(
            Education.objects.order_by("id").values()
        )
        stars = list(
            Education.starred_by.through.objects
            .order_by("education_id", "user_id")
            .values_list("education_id", "user_id")
        )
        return records, stars

    def test_all_roles_can_read_list_and_detail(self):
        for user in (None, self.visitor, self.editor, self.owner):
            with self.subTest(user=user):
                self.client.force_authenticate(user=user)

                response = self.client.get(self.list_url)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(response.data), 1)
                self.assertEqual(
                    response.data[0]["id"],
                    str(self.education.pk),
                )
                self.assertNotIn("fields", response.data[0])

                response = self.client.get(self.detail_url)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    response.data["title"],
                    self.education.title,
                )

    def test_search_is_case_insensitive_and_handles_no_match(self):
        response = self.client.get(
            self.list_url,
            {"title": "  UNIVERSITAS  "},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        response = self.client.get(
            self.list_url,
            {"title": "tidak-ada"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_missing_education_returns_404(self):
        missing_id = uuid.uuid4()
        detail_url = reverse(
            "api:education-detail",
            args=[missing_id],
        )
        star_url = reverse(
            "api:education-star",
            args=[missing_id],
        )

        self.assertEqual(
            self.client.get(detail_url).status_code,
            404,
        )

        self.client.force_authenticate(user=self.owner)
        for method in ("put", "patch", "delete"):
            with self.subTest(method=method):
                response = getattr(self.client, method)(
                    detail_url,
                    self.payload,
                    format="json",
                )
                self.assertEqual(response.status_code, 404)

        self.assertEqual(
            self.client.post(star_url).status_code,
            404,
        )

    def test_guest_and_regular_user_cannot_write(self):
        before = self.database_snapshot()

        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)

            with self.subTest(user=user, method="post"):
                response = self.client.post(
                    self.list_url,
                    self.payload,
                    format="json",
                )
                self.assertEqual(response.status_code, 403)
                self.assertEqual(self.database_snapshot(), before)

            for method in ("put", "patch", "delete"):
                with self.subTest(user=user, method=method):
                    response = getattr(self.client, method)(
                        self.detail_url,
                        self.payload,
                        format="json",
                    )
                    self.assertEqual(response.status_code, 403)
                    self.assertEqual(self.database_snapshot(), before)

    def test_editor_can_patch_and_put_but_not_create_or_delete(self):
        self.client.force_authenticate(user=self.editor)

        response = self.client.patch(
            self.detail_url,
            {"title": "Judul Diperbarui"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.education.refresh_from_db()
        self.assertEqual(self.education.title, "Judul Diperbarui")
        self.assertEqual(
            self.education.description,
            "S1 Sistem Informasi",
        )

        response = self.client.put(
            self.detail_url,
            self.payload,
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.education.refresh_from_db()
        self.assertEqual(
            self.education.description,
            self.payload["description"],
        )

        before = self.database_snapshot()

        response = self.client.post(
            self.list_url,
            self.payload,
            format="json",
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.database_snapshot(), before)

        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.database_snapshot(), before)

    def test_owner_can_create_update_and_delete(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.post(
            self.list_url,
            self.payload,
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        created_id = response.data["id"]
        self.assertTrue(
            Education.objects.filter(pk=created_id).exists()
        )

        detail_url = reverse(
            "api:education-detail",
            args=[created_id],
        )

        response = self.client.patch(
            detail_url,
            {"title": "Judul Baru"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Education.objects.get(pk=created_id).title,
            "Judul Baru",
        )

        response = self.client.put(
            detail_url,
            self.payload,
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Education.objects.get(pk=created_id).title,
            self.payload["title"],
        )

        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b"")
        self.assertFalse(
            Education.objects.filter(pk=created_id).exists()
        )
        self.assertTrue(
            Education.objects.filter(pk=self.education.pk).exists()
        )

    def test_invalid_input_does_not_create_records(self):
        self.client.force_authenticate(user=self.owner)
        before = self.database_snapshot()

        cases = [
            ({"title": "   "}, "title"),
            ({"title": "<b></b>"}, "title"),
            ({"description": "<p> </p>"}, "description"),
            ({"category": "invalid-category"}, "category"),
            ({"thumbnail": "javascript:alert(1)"}, "thumbnail"),
        ]

        for changes, field in cases:
            with self.subTest(field=field, changes=changes):
                response = self.client.post(
                    self.list_url,
                    {**self.payload, **changes},
                    format="json",
                )
                self.assertEqual(response.status_code, 400)
                self.assertIn(field, response.data)
                self.assertEqual(self.database_snapshot(), before)

    def test_html_is_stripped_before_saving(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.post(
            self.list_url,
            {
                **self.payload,
                "title": "<b>Institusi Bersih</b>",
                "description": "<p>Deskripsi bersih</p>",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)

        education = Education.objects.get(pk=response.data["id"])
        self.assertEqual(education.title, "Institusi Bersih")
        self.assertEqual(education.description, "Deskripsi bersih")

    def test_invalid_updates_leave_database_unchanged(self):
        self.client.force_authenticate(user=self.editor)
        before = self.database_snapshot()

        response = self.client.patch(
            self.detail_url,
            {"description": "<p></p>"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.database_snapshot(), before)

        response = self.client.put(
            self.detail_url,
            {"title": "Data tidak lengkap"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("description", response.data)
        self.assertEqual(self.database_snapshot(), before)

    def test_guest_cannot_star(self):
        before = self.database_snapshot()

        response = self.client.post(self.star_url)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.database_snapshot(), before)

    def test_authenticated_roles_can_toggle_their_own_star(self):
        for user in (self.visitor, self.editor, self.owner):
            with self.subTest(user=user):
                self.client.force_authenticate(user=user)
                other_user = (
                    self.visitor if user == self.owner else self.owner
                )

                response = self.client.post(
                    self.star_url,
                    {"user_id": other_user.pk},
                    format="json",
                )
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.data["is_starred"])
                self.assertEqual(response.data["star_count"], 1)
                self.assertEqual(
                    response.data["starred_by_names"],
                    user.username,
                )
                self.assertEqual(
                    list(
                        self.education.starred_by
                        .values_list("pk", flat=True)
                    ),
                    [user.pk],
                )

                response = self.client.post(self.star_url)
                self.assertEqual(response.status_code, 200)
                self.assertFalse(response.data["is_starred"])
                self.assertEqual(response.data["star_count"], 0)
                self.assertFalse(
                    self.education.starred_by.exists()
                )

    def test_star_status_depends_on_current_user(self):
        self.education.starred_by.add(self.visitor)

        for user, expected in (
            (None, False),
            (self.visitor, True),
            (self.editor, False),
        ):
            with self.subTest(user=user):
                self.client.force_authenticate(user=user)
                response = self.client.get(self.detail_url)

                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.data["star_count"], 1)
                self.assertEqual(
                    response.data["is_starred"],
                    expected,
                )
                self.assertNotIn("email", response.data)
                self.assertNotIn("password", response.data)
                self.assertNotIn("starred_by", response.data)

    def test_client_cannot_forge_star_metadata(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.post(
            self.list_url,
            {
                **self.payload,
                "star_count": 99,
                "is_starred": True,
                "starred_by_names": "forged",
                "starred_by": [self.visitor.pk],
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["starred_by_names"], "")
        self.assertFalse(
            Education.objects.get(
                pk=response.data["id"],
            ).starred_by.exists()
        )

    def test_staff_without_editor_group_cannot_edit(self):
        self.visitor.is_staff = True
        self.visitor.save(update_fields=["is_staff"])
        self.client.force_authenticate(user=self.visitor)
        before = self.database_snapshot()

        response = self.client.patch(
            self.detail_url,
            {"title": "Tidak diizinkan"},
            format="json",
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.database_snapshot(), before)

    def test_unsupported_methods_return_405(self):
        self.client.force_authenticate(user=self.owner)
        before = self.database_snapshot()

        self.assertEqual(
            self.client.delete(self.list_url).status_code,
            405,
        )
        self.assertEqual(
            self.client.get(self.star_url).status_code,
            405,
        )
        self.assertEqual(self.database_snapshot(), before)

    def test_session_writes_without_csrf_are_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(
            client.login(
                username="education_owner",
                password="test-password",
            )
        )
        before = self.database_snapshot()

        requests = [
            ("post", self.list_url),
            ("put", self.detail_url),
            ("patch", self.detail_url),
            ("delete", self.detail_url),
            ("post", self.star_url),
        ]

        for method, url in requests:
            with self.subTest(method=method, url=url):
                response = getattr(client, method)(
                    url,
                    self.payload,
                    format="json",
                )
                self.assertEqual(response.status_code, 403)
                self.assertEqual(self.database_snapshot(), before)

    def test_session_create_with_csrf_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(
            client.login(
                username="education_owner",
                password="test-password",
            )
        )

        response = client.get(
            self.list_url,
            HTTP_ACCEPT="text/html",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("csrftoken", client.cookies)
        token = client.cookies["csrftoken"].value

        response = client.post(
            self.list_url,
            self.payload,
            format="json",
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            Education.objects.filter(pk=response.data["id"]).exists()
        )

    def test_education_page_provides_csrf_for_star(self):
        for user in (self.visitor, self.editor):
            with self.subTest(user=user):
                client = APIClient(enforce_csrf_checks=True)
                self.assertTrue(
                    client.login(
                        username=user.username,
                        password="test-password",
                    )
                )
                client.cookies.pop("csrftoken", None)

                response = client.get(reverse("main:show_education"))
                self.assertEqual(response.status_code, 200)
                self.assertIn("csrftoken", client.cookies)
                token = client.cookies["csrftoken"].value

                response = client.post(
                    self.star_url,
                    HTTP_X_CSRFTOKEN=token,
                )
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.data["is_starred"])
                self.assertTrue(
                    self.education.starred_by.filter(pk=user.pk).exists()
                )
