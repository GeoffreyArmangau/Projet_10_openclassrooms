from rest_framework import viewsets, permissions
from django.shortcuts import get_object_or_404
from .serializers import IssueSerializer, CommentSerializer
from projects.models import Contributor, Project
from .models import Issue, Comment
from django.core.exceptions import PermissionDenied
from support.permissions import IsAuthorOrReadOnly, IsContributorOrReadOnly


class IssueViewSet(viewsets.ModelViewSet):
    """
    ViewSet CRUD pour les issues.

    Seuls les contributeurs du projet concerné peuvent accéder aux issues.
    La modification et la suppression sont réservées à l'auteur de l'issue.
    """

    serializer_class = IssueSerializer

    def get_permissions(self):
        """
        Retourne les permissions adaptées à l'action en cours.

        Les actions de modification et suppression requièrent d'être
        l'auteur de l'issue. Les autres actions exigent uniquement d'être
        contributeur du projet.
        """
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnly]
        else:
            permission_classes = [permissions.IsAuthenticated, IsContributorOrReadOnly]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Retourne les issues du projet identifié par project_pk dans l'URL.
        """
        return Issue.objects.filter(project_id=self.kwargs['project_pk'])

    def perform_create(self, serializer):
        """
        Crée une issue sur le projet de l'URL.

        Lève une PermissionDenied si l'assigné n'est pas contributeur du projet.
        """
        project = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        assignee = serializer.validated_data.get('assignee')
        if assignee and not Contributor.objects.filter(user=assignee, project=project).exists():
            raise PermissionDenied("L'assigné doit être contributeur du projet.")
        serializer.save(author=self.request.user, project=project)


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet CRUD pour les commentaires.

    Seuls les contributeurs du projet lié à l'issue peuvent accéder
    aux commentaires. La modification et la suppression sont réservées
    à l'auteur du commentaire.
    """

    serializer_class = CommentSerializer

    def get_permissions(self):
        """
        Retourne les permissions adaptées à l'action en cours.

        Les actions de modification et suppression requièrent d'être
        l'auteur du commentaire. Les autres actions exigent d'être
        contributeur du projet.
        """
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnly]
        else:
            permission_classes = [permissions.IsAuthenticated, IsContributorOrReadOnly]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Retourne les commentaires de l'issue identifiée par issue_pk et project_pk dans l'URL.
        """
        return Comment.objects.filter(
            issue_id=self.kwargs['issue_pk'],
            issue__project_id=self.kwargs['project_pk'],
        )

    def perform_create(self, serializer):
        """
        Crée un commentaire sur l'issue de l'URL.

        Lève une 404 si l'issue n'appartient pas au projet de l'URL.
        """
        issue = get_object_or_404(
            Issue,
            pk=self.kwargs['issue_pk'],
            project_id=self.kwargs['project_pk'],
        )
        serializer.save(author=self.request.user, issue=issue)
