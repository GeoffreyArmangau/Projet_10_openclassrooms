from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import User
from projects.models import Project, Contributor
from .models import Issue, Comment


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

class CommentTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='commentuser', password='commentpass', age=30)
        self.other = User.objects.create_user(username='othercomment', password='otherpass', age=28)
        self.project = Project.objects.create(title='Projet Comment', description='desc', type='back-end', author=self.user)
        Contributor.objects.create(user=self.user, project=self.project)
        Contributor.objects.create(user=self.other, project=self.project)
        self.issue = Issue.objects.create(title='Issue pour commentaire', description='desc', project=self.project, author=self.user, assignee=self.user, priority='LOW', tag='TASK', status='TO_DO')
        self.client.force_authenticate(user=self.user)

    def test_create_comment_success(self):
        url = reverse('comment-list-create')
        data = {
            'description': 'Un commentaire utile',
            'issue': self.issue.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Comment.objects.filter(description='Un commentaire utile').exists())

    def test_create_comment_not_contributor(self):
        outsider = User.objects.create_user(username='outsiderc', password='pass', age=40)
        self.client.force_authenticate(user=outsider)
        url = reverse('comment-list-create')
        data = {
            'description': 'Commentaire refusé',
            'issue': self.issue.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_comments_only_contributor(self):
        Comment.objects.create(description='Commentaire 1', issue=self.issue, author=self.user)
        url = reverse('comment-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['description'], 'Commentaire 1')

    def test_update_comment_only_author(self):
        comment = Comment.objects.create(description='À modifier', issue=self.issue, author=self.user)
        url = reverse('comment-detail', args=[comment.id])
        data = {'description': 'Modifié', 'issue': self.issue.id}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        comment.refresh_from_db()
        self.assertEqual(comment.description, 'Modifié')
        # Test avec un autre utilisateur
        self.client.force_authenticate(user=self.other)
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
