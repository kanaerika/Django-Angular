from django.db import models

# Create your models here.
from django.db import models
from core.models import TimeStampedModel

class Country(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom du pays")
    iso_code = models.CharField(max_length=3, unique=True, verbose_name="Code ISO")

    class Meta:
        verbose_name = "Pays"
        verbose_name_plural = "Pays"

    def __str__(self): return self.name

class City(TimeStampedModel):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='cities', verbose_name="Pays")
    name = models.CharField(max_length=100, verbose_name="Nom de la ville")
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True, verbose_name="Description")
    thumbnail = models.ImageField(upload_to='cities/', blank=True, verbose_name="Image de couverture")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="Latitude")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="Longitude")

    class Meta:
        verbose_name = "Ville"
        verbose_name_plural = "Villes"

    def __str__(self): return f"{self.name}, {self.country.name}"