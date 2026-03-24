from django.shortcuts import render
from rest_framework import generics
from .models import User, Project, Contributor, Issue
from .serializers import UserRegistrationSerializer, ProjectSerializer, IssueSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, permissions
from django.core.exceptions import PermissionDenied

# Create your views here.

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        age = serializer.validated_data.get('age')
        if age is None or age < 15:
            return Response({'error': "L'utilisateur doit avoir au moins 15 ans."}, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

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

class IssueListCreateView(generics.ListCreateAPIView):
    serializer_class = IssueSerializer
    permission_classes = [permissions.IsAuthenticated]

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
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Issue.objects.filter(project__contributor__user=self.request.user)

    def perform_update(self, serializer):
        if self.request.user != self.get_object().author:
            raise PermissionDenied("Seul l'auteur peut modifier cette issue.")
        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user != instance.author:
            raise PermissionDenied("Seul l'auteur peut supprimer cette issue.")
        instance.delete()
