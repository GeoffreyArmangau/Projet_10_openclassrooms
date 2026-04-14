from rest_framework import viewsets, permissions
from .serializers import IssueSerializer, CommentSerializer
from projects.models import Contributor
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
    queryset = Issue.objects.all()

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
        Retourne uniquement les issues des projets dont l'utilisateur est contributeur.
        """
        return Issue.objects.filter(project__contributor__user=self.request.user)

    def perform_create(self, serializer):
        """
        Crée un issue en vérifiant que l'auteur et l'assigné sont contributeurs du projet.

        Lève une PermissionDenied si l'utilisateur courant n'est pas contributeur
        du projet, ou si l'assigné désigné ne l'est pas non plus.
        """
        project = serializer.validated_data['project']
        if not Contributor.objects.filter(user=self.request.user, project=project).exists():
            raise PermissionDenied("Vous devez être contributeur du projet.")
        assignee = serializer.validated_data.get('assignee')
        if assignee and not Contributor.objects.filter(user=assignee, project=project).exists():
            raise PermissionDenied("L'assigné doit être contributeur du projet.")
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet CRUD pour les commentaires.

    Seuls les contributeurs du projet lié à l'issue peuvent accéder
    aux commentaires. La modification et la suppression sont réservées
    à l'auteur du commentaire.
    """

    serializer_class = CommentSerializer
    queryset = Comment.objects.all()

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
        Retourne uniquement les commentaires des issues appartenant aux
        projets dont l'utilisateur est contributeur.
        """
        return Comment.objects.filter(issue__project__contributor__user=self.request.user)

    def perform_create(self, serializer):
        """
        Crée un commentaire en vérifiant que l'utilisateur est contributeur
        du projet auquel appartient l'issue.

        Lève une PermissionDenied si l'utilisateur n'est pas contributeur.
        """
        issue = serializer.validated_data['issue']
        if not Contributor.objects.filter(user=self.request.user, project=issue.project).exists():
            raise PermissionDenied("Vous devez être contributeur du projet pour commenter.")
        serializer.save(author=self.request.user)
