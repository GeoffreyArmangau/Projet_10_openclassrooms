from django.shortcuts import render
from rest_framework import generics
from .models import Project, Contributor
from .serializers import ProjectSerializer
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import PermissionDenied

# Create your views here.

class ProjectListCreateView(generics.ListCreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Seuls les projets où l'utilisateur est contributeur
        return Project.objects.filter(contributor__user=self.request.user)

    def perform_create(self, serializer):
        # L'utilisateur devient author et contributor
        project = serializer.save(author=self.request.user)
        Contributor.objects.create(user=self.request.user, project=project)

class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Project.objects.filter(contributor__user=self.request.user)

    def perform_update(self, serializer):
        # Seul l'auteur peut modifier
        if self.request.user != self.get_object().author:
            raise PermissionDenied("Seul l'auteur peut modifier ce projet.")
        serializer.save()

    def perform_destroy(self, instance):
        # Seul l'auteur peut supprimer
        if self.request.user != instance.author:
            raise PermissionDenied("Seul l'auteur peut supprimer ce projet.")
        instance.delete()
