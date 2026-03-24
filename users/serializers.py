from rest_framework import serializers
from .models import User

class UserRegistrationSerializer(serializers.ModelSerializer):
        
    def validate_age(self, value):
        if value < 15:
            raise serializers.ValidationError("L'utilisateur doit avoir au moins 15 ans pour consentir à la collecte de ses données.")
        return value
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