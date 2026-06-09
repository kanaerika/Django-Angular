from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings
from django.urls import reverse
from core.models import TimeStampedModel
from destinations.models import City

class Category(models.Model):
    name = models.CharField(max_length=50, verbose_name="Nom de la catégorie")
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"

    def __str__(self): return self.name

class Activity(TimeStampedModel):
    # Liens
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='activities', verbose_name="Ville")
    categories = models.ManyToManyField(Category, blank=True, related_name='activities', verbose_name="Catégories")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name="Créé par")
    
    # Informations
    title = models.CharField(max_length=200, verbose_name="Titre")
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField(verbose_name="Description complète")
    what_to_bring = models.TextField(blank=True, verbose_name="Ce qu'il faut apporter")
    
    # Tarification et Logistique
    base_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix de base (Fcfa)")
    max_travelers = models.PositiveIntegerField(default=10, verbose_name="Nombre max de voyageurs")
    duration_hours = models.FloatField(verbose_name="Durée (heures)")
    
    # Statut et SEO
    is_active = models.BooleanField(default=True, verbose_name="Activité active")
    cached_rating = models.FloatField(default=0.0, editable=False, verbose_name="Note moyenne (cache)")

    class Meta:
        verbose_name = "Activité"
        verbose_name_plural = "Activités"
        ordering = ['-created_at']

    def get_absolute_url(self):
        return reverse("tours:detail", kwargs={"slug": self.slug})

    def __str__(self): return self.title

class ActivityImage(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='images', verbose_name="Activité")
    image = models.ImageField(upload_to='activities/%Y/%m/', verbose_name="Fichier image")
    is_cover = models.BooleanField(default=False, verbose_name="Image principale")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")

    class Meta:
        verbose_name = "Image"
        verbose_name_plural = "Images"
        ordering = ['order', 'id']

class Schedule(TimeStampedModel):
    """ Un créneau précis pour une activité """
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='schedules', verbose_name="Activité")
    date = models.DateField(verbose_name="Date")
    start_time = models.TimeField(verbose_name="Heure de début")
    available_spots = models.PositiveIntegerField(verbose_name="Places disponibles")
    
    # Permet de gérer les tarifs dynamiques (ex: plus cher le week-end)
    price_override = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Prix spécifique (€)", help_text="Laisser vide pour utiliser le prix de base")

    class Meta:
        verbose_name = "Créneau"
        verbose_name_plural = "Créneaux"
        # Empêche d'avoir deux fois le même jour à la même heure pour la même activité
        unique_together = ('activity', 'date', 'start_time')
        ordering = ['date', 'start_time']

    def get_actual_price(self):
        """ Retourne le prix override s'il existe, sinon le prix de base """
        return self.price_override if self.price_override else self.activity.base_price

    def __str__(self): return f"{self.activity.title} - {self.date.strftime('%d/%m/%Y')} à {self.start_time.strftime('%H:%M')}"