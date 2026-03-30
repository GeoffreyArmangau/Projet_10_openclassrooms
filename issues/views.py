

from rest_framework import generics, permissions
from .serializers import IssueSerializer, CommentSerializer
from projects.models import Contributor
from .models import Issue, Comment
from django.core.exceptions import PermissionDenied
from support.permissions import IsAuthorOrReadOnly, IsContributorOrReadOnly


class IssueListCreateView(generics.ListCreateAPIView):
    serializer_class = IssueSerializer
    permission_classes = [permissions.IsAuthenticated, IsContributorOrReadOnly]

    def get_queryset(self):
        # Seuls les issues des projets où l'utilisateur est contributeur
        return Issue.objects.filter(project__contributor__user=self.request.user)

    def perform_create(self, serializer):
        project = serializer.validated_data['project']
        # Vérifier que l'utilisateur est contributeur du projet
        if not Contributor.objects.filter(user=self.request.user, project=project).exists():
            raise PermissionDenied("Vous devez être contributeur du projet.")
        # Vérifier que l'assignee est bien contributeur du projet
        assignee = serializer.validated_data.get('assignee')
        if assignee and not Contributor.objects.filter(user=assignee, project=project).exists():
            raise PermissionDenied("L'assigné doit être contributeur du projet.")
        serializer.save(author=self.request.user)


class IssueDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = IssueSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnly]

    def get_queryset(self):
        return Issue.objects.filter(project__contributor__user=self.request.user)

    # Les permissions gèrent déjà l'accès auteur


class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsContributorOrReadOnly]

    def get_queryset(self):
        # Seuls les commentaires des issues des projets où l'utilisateur est contributeur
        return Comment.objects.filter(issue__project__contributor__user=self.request.user)

    def perform_create(self, serializer):
        issue = serializer.validated_data['issue']
        # Vérifier que l'utilisateur est contributeur du projet lié à l'issue
        if not Contributor.objects.filter(user=self.request.user, project=issue.project).exists():
            raise PermissionDenied("Vous devez être contributeur du projet pour commenter.")
        serializer.save(author=self.request.user)


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnly]

    def get_queryset(self):
        return Comment.objects.filter(issue__project__contributor__user=self.request.user)

    # Les permissions gèrent déjà l'accès auteur
