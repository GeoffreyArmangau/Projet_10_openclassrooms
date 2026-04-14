from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Permission accordant les droits complets à l'auteur d'un objet.

    Les utilisateurs authentifiés peuvent lire tous les objets, mais
    seul l'auteur d'un objet peut le modifier ou le supprimer.
    """

    def has_permission(self, request, view):
        """
        Vérifie que l'utilisateur est authentifié pour accéder à la vue.

        Retourne True si l'utilisateur est connecté, False sinon.
        """
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Vérifie que l'utilisateur est l'auteur de l'objet pour les actions
        d'écriture.

        Retourne True pour les méthodes de lecture (GET, HEAD, OPTIONS)
        ou si l'utilisateur courant est l'auteur de l'objet.
        """
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user


class IsContributorOrReadOnly(permissions.BasePermission):
    """
    Permission accordant l'accès en lecture et création aux contributeurs.

    Un contributeur du projet peut lire et créer des objets, mais ne peut
    modifier ou supprimer que les objets rattachés à son projet.
    """

    def has_permission(self, request, view):
        """
        Vérifie que l'utilisateur est authentifié pour accéder à la vue.

        Retourne True si l'utilisateur est connecté, False sinon.
        """
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Vérifie que l'utilisateur est contributeur du projet lié à l'objet
        pour les actions d'écriture.

        Retourne True pour les méthodes de lecture, ou si l'utilisateur
        est contributeur du projet de l'objet. Retourne False si l'objet
        n'a pas d'attribut `project`.
        """
        if request.method in permissions.SAFE_METHODS:
            return True
        if hasattr(obj, 'project'):
            return obj.project.contributor_set.filter(user=request.user).exists()
        return False
