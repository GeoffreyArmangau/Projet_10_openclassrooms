

from rest_framework import viewsets, permissions
from .serializers import IssueSerializer, CommentSerializer
from projects.models import Contributor
from .models import Issue, Comment
from django.core.exceptions import PermissionDenied
from support.permissions import IsAuthorOrReadOnly, IsContributorOrReadOnly



class IssueViewSet(viewsets.ModelViewSet):
    serializer_class = IssueSerializer
    queryset = Issue.objects.all()

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnly]
        else:
            permission_classes = [permissions.IsAuthenticated, IsContributorOrReadOnly]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        return Issue.objects.filter(project__contributor__user=self.request.user)

    def perform_create(self, serializer):
        project = serializer.validated_data['project']
        if not Contributor.objects.filter(user=self.request.user, project=project).exists():
            raise PermissionDenied("Vous devez être contributeur du projet.")
        assignee = serializer.validated_data.get('assignee')
        if assignee and not Contributor.objects.filter(user=assignee, project=project).exists():
            raise PermissionDenied("L'assigné doit être contributeur du projet.")
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnly]
        else:
            permission_classes = [permissions.IsAuthenticated, IsContributorOrReadOnly]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        return Comment.objects.filter(issue__project__contributor__user=self.request.user)

    def perform_create(self, serializer):
        issue = serializer.validated_data['issue']
        if not Contributor.objects.filter(user=self.request.user, project=issue.project).exists():
            raise PermissionDenied("Vous devez être contributeur du projet pour commenter.")
        serializer.save(author=self.request.user)
