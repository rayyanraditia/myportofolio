import uuid

from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from main.models import Project


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
