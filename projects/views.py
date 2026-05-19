from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.http import Http404
from .models import Project, Contributor
from .serializers import ProjectSerializer, ContributorSerializer
from rest_framework.permissions import IsAuthenticated
from support.permissions import IsAuthorOrReadOnly, IsContributorOrReadOnly


class ContributorViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des contributeurs d'un projet.

    Accessible uniquement aux utilisateurs authentifiés. Seul l'auteur
    du projet peut ajouter ou retirer des contributeurs. L'auteur ne peut
    pas se retirer lui-même. Les méthodes PUT et PATCH sont désactivées.
    """

    serializer_class = ContributorSerializer
    http_method_names = ['get', 'post', 'delete', 'head', 'options']

    def get_permissions(self):
        """
        Retourne la liste des permissions pour toutes les actions.

        Toutes les actions nécessitent que l'utilisateur soit authentifié.
        """
        return [IsAuthenticated()]

    def get_project(self):
        """
        Récupère le projet correspondant au `project_pk` fourni dans l'URL.

        Lève une NotFound si aucun projet ne correspond à cet identifiant.
        """
        project_pk = self.kwargs.get('project_pk')
        try:
            return Project.objects.get(pk=project_pk)
        except Project.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound("Projet introuvable.")

    def get_queryset(self):
        """
        Retourne la liste des contributeurs du projet.

        Lève une PermissionDenied si l'utilisateur courant n'est pas
        lui-même contributeur du projet.
        """
        project = self.get_project()
        if not project.contributor_set.filter(user=self.request.user).exists():
            raise Http404
        return Contributor.objects.filter(project=project)

    def perform_create(self, serializer):
        """
        Ajoute un contributeur au projet.

        Lève une PermissionDenied si l'utilisateur courant n'est pas
        l'auteur du projet. Lève une ValidationError si l'utilisateur
        est déjà contributeur du projet.
        """
        project = self.get_project()
        if project.author != self.request.user:
            raise PermissionDenied("Seul l'auteur du projet peut ajouter des contributeurs.")
        user = serializer.validated_data.get('user')
        if Contributor.objects.filter(user=user, project=project).exists():
            raise ValidationError("Cet utilisateur est déjà contributeur du projet.")
        serializer.save(project=project)

    def perform_destroy(self, instance):
        """
        Supprime un contributeur du projet.

        Lève une PermissionDenied si l'utilisateur courant n'est pas
        l'auteur du projet, ou s'il tente de se retirer lui-même
        (l'auteur ne peut pas être retiré des contributeurs).
        """
        project = self.get_project()
        if project.author != self.request.user:
            raise PermissionDenied("Seul l'auteur du projet peut supprimer des contributeurs.")
        if instance.user == project.author:
            raise PermissionDenied("L'auteur du projet ne peut pas être retiré des contributeurs.")
        instance.delete()


class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet CRUD pour les projets.

    Seuls les contributeurs d'un projet peuvent le consulter. La modification
    et la suppression sont réservées à l'auteur du projet. À la création,
    l'utilisateur courant devient automatiquement auteur et premier contributeur.
    """

    serializer_class = ProjectSerializer
    queryset = Project.objects.all()

    def get_permissions(self):
        """
        Retourne les permissions adaptées à l'action en cours.

        Les actions de modification et suppression requièrent d'être
        l'auteur du projet. Les autres actions exigent uniquement d'être
        contributeur.
        """
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]
        else:
            permission_classes = [IsAuthenticated, IsContributorOrReadOnly]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Retourne uniquement les projets dont l'utilisateur est contributeur.
        """
        return Project.objects.filter(contributor__user=self.request.user)

    def perform_create(self, serializer):
        """
        Crée un projet et ajoute automatiquement l'utilisateur courant
        comme auteur et premier contributeur.
        """
        project = serializer.save(author=self.request.user)
        Contributor.objects.create(user=self.request.user, project=project)
