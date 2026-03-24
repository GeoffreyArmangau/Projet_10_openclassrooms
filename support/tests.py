from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status, permissions
from .models import User, Project, Contributor, Issue

# class UserRegistrationTests(APITestCase):
#     def test_register_user_success(self):
#         url = reverse('user-register')
#         data = {
#             'username': 'testolduser',
#             'password': 'testpass123',
#             'email': 'test@example.com',
#             'age': 20,
#             'can_be_contacted': True,
#             'can_data_be_shared': False
#         }
#         response = self.client.post(url, data)
#         print('Réponse inscription:', response.data)
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertTrue(User.objects.filter(username='testuser').exists())

#     def test_register_user_under_15(self):
#         url = reverse('user-register')
#         data = {
#             'username': 'testyounguser',
#             'password': 'testpass123',
#             'email': 'young@example.com',
#             'age': 12,
#             'can_be_contacted': True,
#             'can_data_be_shared': False
#         }
#         response = self.client.post(url, data)
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn('error', response.data)

# class ProjectTests(APITestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(username='projuser', password='projpass', age=25)
#         self.client.force_authenticate(user=self.user)

#     def test_create_project(self):
#         url = reverse('project-list-create')
#         data = {
#             'title': 'Projet Test',
#             'description': 'Description du projet',
#             'type': 'back-end'
#         }
#         response = self.client.post(url, data)
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertTrue(Project.objects.filter(title='Projet Test').exists())
#         self.assertTrue(Contributor.objects.filter(user=self.user, project__title='Projet Test').exists())

#     def test_list_projects_only_contributor(self):
#         # Création d'un projet où l'utilisateur est contributeur
#         project = Project.objects.create(title='Projet 1', description='desc', type='back-end', author=self.user)
#         Contributor.objects.create(user=self.user, project=project)
#         url = reverse('project-list-create')
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data), 1)
#         self.assertEqual(response.data[0]['title'], 'Projet 1')

class IssueTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='issueuser', password='issuepass', age=30)
        self.other = User.objects.create_user(username='otheruser', password='otherpass', age=28)
        self.project = Project.objects.create(title='Projet Issue', description='desc', type='back-end', author=self.user)
        Contributor.objects.create(user=self.user, project=self.project)
        Contributor.objects.create(user=self.other, project=self.project)
        self.client.force_authenticate(user=self.user)

    def test_create_issue_success(self):
        url = reverse('issue-list-create')
        data = {
            'title': 'Bug critique',
            'description': 'Un bug à corriger',
            'project': self.project.id,
            'assignee': self.other.id,
            'priority': 'HIGH',
            'tag': 'BUG',
            'status': 'TO_DO'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Issue.objects.filter(title='Bug critique').exists())

    def test_create_issue_assignee_not_contributor(self):
        outsider = User.objects.create_user(username='outsider', password='pass', age=40)
        url = reverse('issue-list-create')
        data = {
            'title': 'Bug',
            'description': 'desc',
            'project': self.project.id,
            'assignee': outsider.id,
            'priority': 'LOW',
            'tag': 'BUG',
            'status': 'TO_DO'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_issues_only_contributor(self):
        Issue.objects.create(title='Tâche 1', description='desc', project=self.project, author=self.user, assignee=self.user, priority='LOW', tag='TASK', status='TO_DO')
        url = reverse('issue-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Tâche 1')

    def test_update_issue_only_author(self):
        issue = Issue.objects.create(title='Tâche 2', description='desc', project=self.project, author=self.user, assignee=self.user, priority='LOW', tag='TASK', status='TO_DO')
        url = reverse('issue-detail', args=[issue.id])
        data = {'title': 'Tâche modifiée', 'description': 'desc', 'project': self.project.id, 'assignee': self.user.id, 'priority': 'LOW', 'tag': 'TASK', 'status': 'IN_PROGRESS'}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        issue.refresh_from_db()
        self.assertEqual(issue.title, 'Tâche modifiée')
        # Test avec un autre utilisateur
        self.client.force_authenticate(user=self.other)
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
