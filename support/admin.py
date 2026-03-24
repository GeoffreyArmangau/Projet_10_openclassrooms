from django.contrib import admin
from users.models import User
from projects.models import Project, Contributor
from issues.models import Issue, Comment

admin.site.register(User)
admin.site.register(Project)
admin.site.register(Contributor)
admin.site.register(Issue)
admin.site.register(Comment)
