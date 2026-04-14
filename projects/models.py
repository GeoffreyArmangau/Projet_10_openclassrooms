from django.db import models


class Project(models.Model):
    """
    Représente un projet de développement logiciel.

    Un projet est créé par un auteur et peut être de différents types
    (back-end, front-end, iOS, Android). L'auteur est automatiquement
    ajouté comme contributeur à la création.
    """

    TYPE_CHOICES = [
        ('back-end', 'Back-end'),
        ('front-end', 'Front-end'),
        ('iOS', 'iOS'),
        ('Android', 'Android'),
    ]
    title = models.CharField(max_length=128)
    description = models.TextField()
    type = models.CharField(max_length=16, choices=TYPE_CHOICES)
    author = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='projects')
    created_time = models.DateTimeField(auto_now_add=True)


class Contributor(models.Model):
    """
    Représente le lien entre un utilisateur et un projet auquel il contribue.

    La contrainte `unique_together` garantit qu'un même utilisateur ne peut
    être ajouté qu'une seule fois comme contributeur d'un projet donné.
    """

    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Métadonnées du modèle Contributor."""

        unique_together = ('user', 'project')
