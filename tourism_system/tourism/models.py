from django.db import models
from django.conf import settings

class Destination(models.Model):
    name = models.CharField(max_length=150)
    city = models.CharField(max_length=180)
    description = models.TextField()
    image = models.ImageField(upload_to='destination/')
    created_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Destination"
        verbose_name_plural = "Destinations"
    
    def __str__(self):
        return self.name


class Hotel(models.Model):
    name = models.CharField(max_length=150)
    address = models.CharField(max_length=180)
    image = models.ImageField(upload_to='hotels/')
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='hotels')
    
    class Meta:
        verbose_name = "Hôtel"
        verbose_name_plural = "Hôtels"
    
    def __str__(self):
        return self.name


class HotelBooking(models.Model):
    """Réservation d'hôtel - nommée différemment pour éviter conflit avec booking app"""
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('confirmed', 'Confirmée'),
        ('cancelled', 'Annulée'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='hotel_bookings')
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='bookings')
    check_in = models.DateField()
    check_out = models.DateField()
    guests = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Réservation d'hôtel"
        verbose_name_plural = "Réservations d'hôtels"

    def __str__(self):
        return f"{self.user.username} - {self.hotel.name}"


class DestinationReview(models.Model):
    """Avis sur destination - nommée différemment pour éviter conflit avec reviews app"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='destination_reviews')
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField()  # 1–5
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Avis sur destination"
        verbose_name_plural = "Avis sur destinations"
        unique_together = ('user', 'destination')

    def __str__(self):
        return f"Avis de {self.user.username} sur {self.destination.name}"