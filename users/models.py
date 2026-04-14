from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Modèle utilisateur personnalisé étendant AbstractUser.

    Ajoute des champs RGPD (âge, consentement de contact, consentement
    de partage des données) au modèle utilisateur Django standard.
    L'âge minimum requis pour s'inscrire est de 15 ans.
    """

    age = models.PositiveIntegerField()
    can_be_contacted = models.BooleanField(default=False)
    can_data_be_shared = models.BooleanField(default=False)
