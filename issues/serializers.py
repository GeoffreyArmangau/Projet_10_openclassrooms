from rest_framework import serializers
from .models import Issue, Comment

class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = [
            'id', 'title', 'description', 'project', 'author', 'assignee',
            'priority', 'tag', 'status', 'created_time'
        ]
        read_only_fields = ['author', 'created_time']

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            'id', 'uuid', 'description', 'author', 'issue', 'created_time'
        ]
        read_only_fields = ['author', 'uuid', 'created_time']