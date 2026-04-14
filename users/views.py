from rest_framework import generics, viewsets, status
from .models import User
from .serializers import UserRegistrationSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from support.permissions import IsAuthorOrReadOnly
from rest_framework.response import Response


class UserRegistrationView(generics.CreateAPIView):
    """
    Vue d'inscription ouverte à tous les utilisateurs non authentifiés.

    Permet la création d'un nouveau compte utilisateur. Accessible sans
    authentification (permission AllowAny).
    """

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request):
        """
        Traite la requête d'inscription et retourne les données du nouvel utilisateur.

        Valide les données soumises via le sérialiseur, crée le compte,
        puis retourne une réponse HTTP 201 avec les données de l'utilisateur créé.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet CRUD pour la gestion du profil utilisateur.

    Un utilisateur standard ne peut consulter et modifier que son propre
    profil. Un superutilisateur a accès à tous les profils. La modification
    et la suppression sont réservées à l'utilisateur lui-même.
    """

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer

    def get_permissions(self):
        """
        Retourne les permissions adaptées à l'action en cours.

        Les actions de modification et suppression requièrent d'être
        l'auteur du profil. Les autres actions exigent uniquement
        d'être authentifié.
        """
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Retourne le queryset d'utilisateurs accessible à l'utilisateur courant.

        Un superutilisateur voit tous les comptes. Un utilisateur standard
        ne voit que son propre profil.
        """
        user = self.request.user
        if user.is_superuser:
            return User.objects.all()
        return User.objects.filter(id=user.id)
