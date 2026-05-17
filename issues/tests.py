from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import User
from projects.models import Project, Contributor
from .models import Issue, Comment


class IssueTests(APITestCase):
    """Tests fonctionnels pour l'API des issues."""

    def setUp(self):
        """
        Initialise les données de test communes à tous les tests d'issues.

        Crée deux utilisateurs, un projet et les ajoute tous les deux
        comme contributeurs. Authentifie le client avec le premier utilisateur.
        """
        self.user = User.objects.create_user(username='issueuser', password='issuepass', age=30)
        self.other = User.objects.create_user(username='otheruser', password='otherpass', age=28)
        self.project = Project.objects.create(title='Projet Issue', description='desc', type='back-end', author=self.user)
        Contributor.objects.create(user=self.user, project=self.project)
        Contributor.objects.create(user=self.other, project=self.project)
        self.client.force_authenticate(user=self.user)

    def test_create_issue_success(self):
        """
        Vérifie qu'un contributeur peut créer un issue avec un assigné valide.

        Attend une réponse HTTP 201 et la présence de l'issue en base.
        """
        url = reverse('issue-list', kwargs={'project_pk': self.project.id})
        data = {
            'title': 'Bug critique',
            'description': 'Un bug à corriger',
            'assignee': self.other.id,
            'priority': 'HIGH',
            'tag': 'BUG',
            'status': 'TO_DO'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Issue.objects.filter(title='Bug critique').exists())

    def test_create_issue_assignee_not_contributor(self):
        """
        Vérifie qu'un issue ne peut pas être assigné à un non-contributeur.

        Attend une réponse HTTP 403 lorsque l'assigné n'appartient pas au projet.
        """
        outsider = User.objects.create_user(username='outsider', password='pass', age=40)
        url = reverse('issue-list', kwargs={'project_pk': self.project.id})
        data = {
            'title': 'Bug',
            'description': 'desc',
            'assignee': outsider.id,
            'priority': 'LOW',
            'tag': 'BUG',
            'status': 'TO_DO'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_issues_only_contributor(self):
        """
        Vérifie qu'un contributeur ne voit que les issues de ses projets.

        Attend une réponse HTTP 200 avec uniquement l'issue du projet
        auquel l'utilisateur contribue.
        """
        Issue.objects.create(title='Tâche 1', description='desc', project=self.project, author=self.user, assignee=self.user, priority='LOW', tag='TASK', status='TO_DO')
        url = reverse('issue-list', kwargs={'project_pk': self.project.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Tâche 1')

    def test_update_issue_only_author(self):
        """
        Vérifie que seul l'auteur d'un issue peut le modifier.

        Attend une réponse HTTP 200 pour l'auteur et HTTP 403 pour un
        autre contributeur tentant de modifier le même issue.
        """
        issue = Issue.objects.create(title='Tâche 2', description='desc', project=self.project, author=self.user, assignee=self.user, priority='LOW', tag='TASK', status='TO_DO')
        url = reverse('issue-detail', kwargs={'project_pk': self.project.id, 'pk': issue.id})
        data = {'title': 'Tâche modifiée', 'description': 'desc', 'assignee': self.user.id, 'priority': 'LOW', 'tag': 'TASK', 'status': 'IN_PROGRESS'}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        issue.refresh_from_db()
        self.assertEqual(issue.title, 'Tâche modifiée')
        # Test avec un autre utilisateur
        self.client.force_authenticate(user=self.other)
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CommentTests(APITestCase):
    """Tests fonctionnels pour l'API des commentaires."""

    def setUp(self):
        """
        Initialise les données de test communes à tous les tests de commentaires.

        Crée deux utilisateurs, un projet, les ajoute comme contributeurs,
        et crée un issue sur lequel les tests vont commenter.
        """
        self.user = User.objects.create_user(username='commentuser', password='commentpass', age=30)
        self.other = User.objects.create_user(username='othercomment', password='otherpass', age=28)
        self.project = Project.objects.create(title='Projet Comment', description='desc', type='back-end', author=self.user)
        Contributor.objects.create(user=self.user, project=self.project)
        Contributor.objects.create(user=self.other, project=self.project)
        self.issue = Issue.objects.create(title='Issue pour commentaire', description='desc', project=self.project, author=self.user, assignee=self.user, priority='LOW', tag='TASK', status='TO_DO')
        self.client.force_authenticate(user=self.user)

    def test_create_comment_success(self):
        """
        Vérifie qu'un contributeur peut poster un commentaire sur un issue.

        Attend une réponse HTTP 201 et la présence du commentaire en base.
        """
        url = reverse('comment-list', kwargs={'project_pk': self.project.id, 'issue_pk': self.issue.id})
        data = {
            'description': 'Un commentaire utile',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Comment.objects.filter(description='Un commentaire utile').exists())

    def test_create_comment_not_contributor(self):
        """
        Vérifie qu'un non-contributeur ne peut pas poster de commentaire.

        Attend une réponse HTTP 404 lorsque l'utilisateur n'est pas
        contributeur du projet lié à l'issue.
        """
        outsider = User.objects.create_user(username='outsiderc', password='pass', age=40)
        self.client.force_authenticate(user=outsider)
        url = reverse('comment-list', kwargs={'project_pk': self.project.id, 'issue_pk': self.issue.id})
        data = {
            'description': 'Commentaire refusé',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_comments_only_contributor(self):
        """
        Vérifie qu'un contributeur ne voit que les commentaires de ses projets.

        Attend une réponse HTTP 200 avec uniquement le commentaire de l'issue
        appartenant au projet où l'utilisateur est contributeur.
        """
        Comment.objects.create(description='Commentaire 1', issue=self.issue, author=self.user)
        url = reverse('comment-list', kwargs={'project_pk': self.project.id, 'issue_pk': self.issue.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['description'], 'Commentaire 1')

    def test_update_comment_only_author(self):
        """
        Vérifie que seul l'auteur d'un commentaire peut le modifier.

        Attend une réponse HTTP 200 pour l'auteur et HTTP 403 pour un
        autre contributeur tentant de modifier le même commentaire.
        """
        comment = Comment.objects.create(description='À modifier', issue=self.issue, author=self.user)
        url = reverse('comment-detail', kwargs={'project_pk': self.project.id, 'issue_pk': self.issue.id, 'pk': comment.id})
        data = {'description': 'Modifié'}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        comment.refresh_from_db()
        self.assertEqual(comment.description, 'Modifié')
        # Test avec un autre utilisateur
        self.client.force_authenticate(user=self.other)
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
