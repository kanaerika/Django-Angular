from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models
from core.models import TimeStampedModel

class Role(TimeStampedModel):
    name = models.CharField(max_length=50, unique=True, verbose_name="Nom du rôle")
    description = models.TextField(blank=True, verbose_name="Description")
    
    class Meta:
        verbose_name = "Rôle"
        verbose_name_plural = "Rôles"

    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    role = models.ForeignKey(
        Role, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Rôle",
        related_name='users'
    )

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

class Profile(TimeStampedModel):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile', verbose_name="Utilisateur")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Téléphone")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name="Photo de profil")
    bio = models.TextField(blank=True, verbose_name="Biographie")
    
    class Meta:
        verbose_name = "Profil"

    def __str__(self):
        return f"Profil de {self.user.get_full_name()}"