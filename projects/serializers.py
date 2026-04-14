from rest_framework import serializers
from .models import Project, Contributor


class ProjectSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour le modèle Project.

    Expose les informations principales d'un projet. Les champs `author`
    et `created_time` sont en lecture seule et définis automatiquement
    lors de la création.
    """

    class Meta:
        """Métadonnées du sérialiseur ProjectSerializer."""

        model = Project
        fields = ['id', 'title', 'description', 'type', 'author', 'created_time']
        read_only_fields = ['author', 'created_time']


class ContributorSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour le modèle Contributor.

    Expose les informations d'un lien contributeur-projet. Les champs
    `project` et `created_time` sont en lecture seule ; le projet est
    déterminé automatiquement via l'URL.
    """

    class Meta:
        """Métadonnées du sérialiseur ContributorSerializer."""

        model = Contributor
        fields = ['id', 'user', 'project', 'created_time']
        read_only_fields = ['project', 'created_time']
