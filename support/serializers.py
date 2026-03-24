from rest_framework import serializers
from .models import User, Project, Contributor, Issue, Comment

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'age', 'can_be_contacted', 'can_data_be_shared')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            age=validated_data['age'],
            can_be_contacted=validated_data.get('can_be_contacted', False),
            can_data_be_shared=validated_data.get('can_data_be_shared', False),
        )
        return user

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'type', 'author', 'created_time']
        read_only_fields = ['author', 'created_time']

class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = [
            'id', 'title', 'description', 'project', 'author', 'assignee',
            'priority', 'tag', 'status', 'created_time'
        ]
        read_only_fields = ['author', 'created_time']
