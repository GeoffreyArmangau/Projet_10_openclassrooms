from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError
from .models import Project, Contributor
from .serializers import ProjectSerializer, ContributorSerializer
from rest_framework.permissions import IsAuthenticated
from support.permissions import IsAuthorOrReadOnly, IsContributorOrReadOnly


class ContributorViewSet(viewsets.ModelViewSet):
    serializer_class = ContributorSerializer
    http_method_names = ['get', 'post', 'delete', 'head', 'options']

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]
        else:
            permission_classes = [IsAuthenticated, IsContributorOrReadOnly]
        return [permission() for permission in permission_classes]

    def get_project(self):
        project_pk = self.kwargs.get('project_pk')
        try:
            return Project.objects.get(pk=project_pk)
        except Project.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound("Projet introuvable.")

    def get_queryset(self):
        project = self.get_project()
        # Seuls les contributeurs du projet peuvent lister
        if not project.contributor_set.filter(user=self.request.user).exists():
            raise PermissionDenied("Vous n'êtes pas contributeur de ce projet.")
        return Contributor.objects.filter(project=project)

    def perform_create(self, serializer):
        project = self.get_project()
        # Seul l'auteur du projet peut ajouter des contributeurs
        if project.author != self.request.user:
            raise PermissionDenied("Seul l'auteur du projet peut ajouter des contributeurs.")
        user = serializer.validated_data.get('user')
        if Contributor.objects.filter(user=user, project=project).exists():
            raise ValidationError("Cet utilisateur est déjà contributeur du projet.")
        serializer.save(project=project)

    def perform_destroy(self, instance):
        project = self.get_project()
        # Seul l'auteur du projet peut supprimer des contributeurs
        if project.author != self.request.user:
            raise PermissionDenied("Seul l'auteur du projet peut supprimer des contributeurs.")
        # L'auteur ne peut pas se retirer lui-même
        if instance.user == project.author:
            raise PermissionDenied("L'auteur du projet ne peut pas être retiré des contributeurs.")
        instance.delete()


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]
        else:
            permission_classes = [IsAuthenticated, IsContributorOrReadOnly]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        # Seuls les projets où l'utilisateur est contributeur
        return Project.objects.filter(contributor__user=self.request.user)

    def perform_create(self, serializer):
        # L'utilisateur devient author et contributor
        project = serializer.save(author=self.request.user)
        Contributor.objects.create(user=self.request.user, project=project)
