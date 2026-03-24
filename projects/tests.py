from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import User
from .models import Project, Contributor

class ProjectTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='projuser', password='projpass', age=25)
        self.client.force_authenticate(user=self.user)

    def test_create_project(self):
        url = reverse('project-list-create')
        data = {
            'title': 'Projet Test',
            'description': 'Description du projet',
            'type': 'back-end'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Project.objects.filter(title='Projet Test').exists())
        self.assertTrue(Contributor.objects.filter(user=self.user, project__title='Projet Test').exists())

    def test_list_projects_only_contributor(self):
        # Création d'un projet où l'utilisateur est contributeur
        project = Project.objects.create(title='Projet 1', description='desc', type='back-end', author=self.user)
        Contributor.objects.create(user=self.user, project=project)
        url = reverse('project-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Projet 1')