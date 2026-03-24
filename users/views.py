from django.shortcuts import render
from rest_framework import generics, viewsets
from .models import User
from .serializers import UserRegistrationSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import PermissionDenied

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer

    def get_permissions(self):
        if self.action in ['create']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        # Un utilisateur ne peut voir que son propre profil (sauf admin)
        user = self.request.user
        if user.is_superuser:
            return User.objects.all()
        return User.objects.filter(id=user.id)

    def perform_update(self, serializer):
        # Un utilisateur ne peut modifier que son propre profil
        if self.request.user != self.get_object():
            raise PermissionDenied("Vous ne pouvez modifier que votre propre profil.")
        serializer.save()

    def perform_destroy(self, instance):
        # Un utilisateur ne peut supprimer que son propre profil
        if self.request.user != instance:
            raise PermissionDenied("Vous ne pouvez supprimer que votre propre profil.")
        instance.delete()

