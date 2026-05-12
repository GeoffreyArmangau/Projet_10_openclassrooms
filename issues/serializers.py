from rest_framework import serializers
from .models import Issue, Comment


class IssueSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour le modèle Issue.

    Expose les champs principaux d'un issue. Les champs `author` et
    `created_time` sont en lecture seule et définis automatiquement
    lors de la création.
    """

    class Meta:
        """Métadonnées du sérialiseur IssueSerializer."""

        model = Issue
        fields = [
            'id', 'title', 'description', 'project', 'author', 'assignee',
            'priority', 'tag', 'status', 'created_time'
        ]
        read_only_fields = ['author', 'created_time', 'project']


class CommentSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour le modèle Comment.

    Expose les champs d'un commentaire. Les champs `author`, `uuid` et
    `created_time` sont en lecture seule et définis automatiquement.
    """

    class Meta:
        """Métadonnées du sérialiseur CommentSerializer."""

        model = Comment
        fields = [
            'id', 'uuid', 'description', 'author', 'issue', 'created_time'
        ]
        read_only_fields = ['author', 'uuid', 'created_time', 'issue']
