from rest_framework import permissions

class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    L'auteur a tous les droits, les autres peuvent seulement lire.
    """
    def has_object_permission(self, request, view, obj):
        # Lecture autorisée pour tous les utilisateurs authentifiés
        if request.method in permissions.SAFE_METHODS:
            return True
        # Modification/suppression autorisée seulement pour l'auteur
        return obj.author == request.user

class IsContributorOrReadOnly(permissions.BasePermission):
    """
    Un contributeur peut lire, créer, mais ne peut modifier/supprimer que ses propres objets.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        # Pour les objets liés à un projet, vérifier la contribution
        if hasattr(obj, 'project'):
            return obj.project.contributor_set.filter(user=request.user).exists()
        return False
