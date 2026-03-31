from rest_framework import viewsets
from .models import Project, Contributor
from .serializers import ProjectSerializer
from rest_framework.permissions import IsAuthenticated
from support.permissions import IsAuthorOrReadOnly, IsContributorOrReadOnly



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
