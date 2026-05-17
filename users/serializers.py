from rest_framework import serializers
from .models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour l'inscription d'un nouvel utilisateur.

    Valide les données d'enregistrement, vérifie que l'utilisateur a au
    moins 15 ans (conformité RGPD), et crée le compte avec un mot de passe
    correctement haché.
    """

    password = serializers.CharField(write_only=True)

    class Meta:
        """Métadonnées du sérialiseur UserRegistrationSerializer."""

        model = User
        fields = ('username', 'password', 'email', 'age', 'can_be_contacted', 'can_data_be_shared')

    def validate_age(self, value):
        """
        Valide que l'utilisateur a au moins 15 ans.

        Lève une ValidationError si l'âge est inférieur à 15 ans,
        conformément aux exigences RGPD de consentement.
        """
        if value < 15:
            raise serializers.ValidationError("L'utilisateur doit avoir au moins 15 ans pour consentir à la collecte de ses données.")
        return value

    def update(self, instance, validated_data):
        """
        Met à jour le profil utilisateur en hachant le mot de passe si fourni.
        """
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

    def create(self, validated_data):
        """
        Crée et retourne un nouvel utilisateur avec un mot de passe haché.

        Utilise `create_user` pour s'assurer que le mot de passe est
        correctement haché et non stocké en clair.
        """
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            age=validated_data['age'],
            can_be_contacted=validated_data.get('can_be_contacted', False),
            can_data_be_shared=validated_data.get('can_data_be_shared', False),
        )
        return user
