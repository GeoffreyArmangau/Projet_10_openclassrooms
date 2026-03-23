from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class User(AbstractUser):
	age = models.PositiveIntegerField()
	can_be_contacted = models.BooleanField(default=False)
	can_data_be_shared = models.BooleanField(default=False)

class Project(models.Model):
	TYPE_CHOICES = [
		('back-end', 'Back-end'),
		('front-end', 'Front-end'),
		('iOS', 'iOS'),
		('Android', 'Android'),
	]
	title = models.CharField(max_length=128)
	description = models.TextField()
	type = models.CharField(max_length=16, choices=TYPE_CHOICES)
	author = models.ForeignKey('User', on_delete=models.CASCADE, related_name='projects')
	created_time = models.DateTimeField(auto_now_add=True)

class Contributor(models.Model):
	user = models.ForeignKey('User', on_delete=models.CASCADE)
	project = models.ForeignKey('Project', on_delete=models.CASCADE)
	class Meta:
		unique_together = ('user', 'project')

class Issue(models.Model):
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
	project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='issues')
	author = models.ForeignKey('User', on_delete=models.CASCADE, related_name='issues')
	assignee = models.ForeignKey('User', on_delete=models.CASCADE, related_name='assigned_issues')
	priority = models.CharField(max_length=6, choices=PRIORITY_CHOICES)
	tag = models.CharField(max_length=8, choices=TAG_CHOICES)
	status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='TO_DO')
	created_time = models.DateTimeField(auto_now_add=True)

class Comment(models.Model):
	uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
	description = models.TextField()
	author = models.ForeignKey('User', on_delete=models.CASCADE, related_name='comments')
	issue = models.ForeignKey('Issue', on_delete=models.CASCADE, related_name='comments')
	created_time = models.DateTimeField(auto_now_add=True)
