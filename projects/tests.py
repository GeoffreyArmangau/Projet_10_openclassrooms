from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import User
from .models import Project, Contributor


class ProjectTests(APITestCase):
    """Tests fonctionnels pour l'API des projets."""

    def setUp(self):
        """
        Initialise les données de test communes à tous les tests de projets.

        Crée un utilisateur et authentifie le client avec celui-ci.
        """
        self.user = User.objects.create_user(username='projuser', password='projpass', age=25)
        self.client.force_authenticate(user=self.user)

    def test_create_project(self):
        """
        Vérifie qu'un utilisateur authentifié peut créer un projet.

        Attend une réponse HTTP 201, la présence du projet en base, et
        que l'utilisateur est automatiquement ajouté comme contributeur.
        """
        url = reverse('project-list')
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
        """
        Vérifie qu'un utilisateur ne voit que les projets auxquels il contribue.

        Attend une réponse HTTP 200 avec uniquement le projet où l'utilisateur
        est enregistré comme contributeur.
        """
        project = Project.objects.create(title='Projet 1', description='desc', type='back-end', author=self.user)
        Contributor.objects.create(user=self.user, project=project)
        url = reverse('project-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Projet 1')


class ContributorTests(APITestCase):
    """Tests fonctionnels pour l'API des contributeurs d'un projet."""

    def setUp(self):
        """
        Initialise les données de test communes à tous les tests de contributeurs.

        Crée trois utilisateurs (auteur, autre utilisateur, nouvel utilisateur),
        un projet avec l'auteur comme seul contributeur initial, et l'URL
        de liste des contributeurs.
        """
        self.author = User.objects.create_user(username='author', password='pass', age=25)
        self.other_user = User.objects.create_user(username='other', password='pass', age=25)
        self.new_user = User.objects.create_user(username='newuser', password='pass', age=25)

        self.project = Project.objects.create(
            title='Projet Test',
            description='desc',
            type='back-end',
            author=self.author
        )
        Contributor.objects.create(user=self.author, project=self.project)

        self.list_url = reverse('contributor-list', kwargs={'project_pk': self.project.pk})

    def detail_url(self, contributor_pk):
        """
        Retourne l'URL de détail d'un contributeur pour le projet courant.

        Args:
            contributor_pk: La clé primaire du contributeur.
        """
        return reverse('contributor-detail', kwargs={
            'project_pk': self.project.pk,
            'pk': contributor_pk
        })

    # --- LIST ---

    def test_auteur_peut_lister_contributeurs(self):
        """Vérifie que l'auteur du projet peut lister les contributeurs (HTTP 200)."""
        self.client.force_authenticate(user=self.author)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_non_contributeur_ne_peut_pas_lister(self):
        """Vérifie qu'un non-contributeur ne peut pas lister les contributeurs (HTTP 403)."""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_authentifie_ne_peut_pas_lister(self):
        """Vérifie qu'un utilisateur non authentifié ne peut pas lister les contributeurs (HTTP 401)."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- CREATE ---

    def test_auteur_peut_ajouter_contributeur(self):
        """Vérifie que l'auteur du projet peut ajouter un nouveau contributeur (HTTP 201)."""
        self.client.force_authenticate(user=self.author)
        data = {'user': self.new_user.pk}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Contributor.objects.filter(user=self.new_user, project=self.project).exists())

    def test_non_auteur_ne_peut_pas_ajouter_contributeur(self):
        """
        Vérifie qu'un contributeur non-auteur ne peut pas ajouter d'autres contributeurs (HTTP 403).
        """
        Contributor.objects.create(user=self.other_user, project=self.project)
        self.client.force_authenticate(user=self.other_user)
        data = {'user': self.new_user.pk}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Contributor.objects.filter(user=self.new_user, project=self.project).exists())

    def test_non_authentifie_ne_peut_pas_ajouter_contributeur(self):
        """Vérifie qu'un utilisateur non authentifié ne peut pas ajouter un contributeur (HTTP 401)."""
        data = {'user': self.new_user.pk}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_ajout_doublon_contributeur_interdit(self):
        """
        Vérifie qu'un utilisateur déjà contributeur ne peut pas être ajouté une seconde fois.

        Attend un statut HTTP 400 ou 403 selon la logique de validation.
        """
        self.client.force_authenticate(user=self.author)
        data = {'user': self.author.pk}
        response = self.client.post(self.list_url, data)
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN])

    def test_auteur_ne_peut_pas_se_supprimer_lui_meme(self):
        """
        Vérifie que l'auteur du projet ne peut pas se retirer des contributeurs (HTTP 403).
        """
        contributor = Contributor.objects.get(user=self.author, project=self.project)
        self.client.force_authenticate(user=self.author)
        response = self.client.delete(self.detail_url(contributor.pk))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Contributor.objects.filter(pk=contributor.pk).exists())

    # --- DELETE ---

    def test_auteur_peut_supprimer_contributeur(self):
        """Vérifie que l'auteur du projet peut retirer un contributeur (HTTP 204)."""
        contributor = Contributor.objects.create(user=self.other_user, project=self.project)
        self.client.force_authenticate(user=self.author)
        response = self.client.delete(self.detail_url(contributor.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Contributor.objects.filter(pk=contributor.pk).exists())

    def test_non_auteur_ne_peut_pas_supprimer_contributeur(self):
        """
        Vérifie qu'un contributeur non-auteur ne peut pas retirer un autre contributeur (HTTP 403).
        """
        contributor = Contributor.objects.create(user=self.new_user, project=self.project)
        Contributor.objects.create(user=self.other_user, project=self.project)
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(self.detail_url(contributor.pk))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Contributor.objects.filter(pk=contributor.pk).exists())

    def test_non_authentifie_ne_peut_pas_supprimer_contributeur(self):
        """Vérifie qu'un utilisateur non authentifié ne peut pas supprimer un contributeur (HTTP 401)."""
        contributor = Contributor.objects.create(user=self.other_user, project=self.project)
        response = self.client.delete(self.detail_url(contributor.pk))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
