from django.db import models


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
	author = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='projects')
	created_time = models.DateTimeField(auto_now_add=True)
	
class Contributor(models.Model):
	user = models.ForeignKey('users.User', on_delete=models.CASCADE)
	project = models.ForeignKey('projects.Project', on_delete=models.CASCADE)
	class Meta:
		unique_together = ('user', 'project')