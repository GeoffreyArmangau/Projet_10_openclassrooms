from django.db import models
import uuid


class Issue(models.Model):
    """
    Représente un problème (bug, feature ou tâche) rattaché à un projet.

    Un issue possède une priorité, un tag et un statut.
    Il est créé par un auteur (contributeur du projet) et peut être
    assigné à un autre contributeur.
    """

    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
    ]
    TAG_CHOICES = [
        ('BUG', 'Bug'),
        ('FEATURE', 'Feature'),
        ('TASK', 'Task'),
    ]
    STATUS_CHOICES = [
        ('TO_DO', 'To Do'),
        ('IN_PROGRESS', 'In Progress'),
        ('FINISHED', 'Finished'),
    ]
    title = models.CharField(max_length=128)
    description = models.TextField()
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='issues')
    author = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='issues')
    assignee = models.ForeignKey('users.User', on_delete=models.SET_NULL, related_name='assigned_issues', null=True, blank=True)
    priority = models.CharField(max_length=6, choices=PRIORITY_CHOICES)
    tag = models.CharField(max_length=8, choices=TAG_CHOICES)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='TO_DO')
    created_time = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    """
    Représente un commentaire posté sur un issue.

    Chaque commentaire est identifié par un UUID unique (en plus de son id)
    et est lié à un issue et à son auteur.
    """

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    description = models.TextField()
    author = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='comments')
    issue = models.ForeignKey('issues.Issue', on_delete=models.CASCADE, related_name='comments')
    created_time = models.DateTimeField(auto_now_add=True)
