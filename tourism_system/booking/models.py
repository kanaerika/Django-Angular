from django.db import models

# Create your models here.
import uuid
from django.db import models
from django.conf import settings
from core.models import TimeStampedModel
from tour.models import Schedule

class Booking(TimeStampedModel):
    STATUS_CHOICES = [
        ('pending', 'En attente de paiement'),
        ('confirmed', 'Confirmée'),
        ('completed', 'Terminée'), # Très important pour autoriser l'avis
        ('cancelled', 'Annulée'),
        ('refunded', 'Remboursée'),
    ]
    
    booking_reference = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="Référence de réservation")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings', verbose_name="Voyageur")
    schedule = models.ForeignKey(Schedule, on_delete=models.PROTECT, verbose_name="Créneau réservé")
    
    number_of_travelers = models.PositiveIntegerField(default=1, verbose_name="Nombre de voyageurs")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix total payé (€)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Statut")
    special_requests = models.TextField(blank=True, verbose_name="Demandes spéciales")

    class Meta:
        verbose_name = "Réservation"
        verbose_name_plural = "Réservations"

    def save(self, *args, **kwargs):
        # On calcule le prix en se basant sur la méthode propre du modèle Schedule
        if not self.pk:
            self.total_price = self.number_of_travelers * self.schedule.get_actual_price()
        super().save(*args, **kwargs)

    def __str__(self): return f"Réservation {str(self.booking_reference)[:8]}..."

class Payment(TimeStampedModel):
    METHOD_CHOICES = [
        ('stripe', 'Carte bancaire (Stripe)'),
        ('paypal', 'PayPal'),
        ('wire', 'Virement bancaire'),
    ]
    
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment', verbose_name="reservation linked")
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default='stripe', verbose_name="payment mode")
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, verbose_name="ID of the transaction")
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="amount payed in (FCFA)")
    is_successful = models.BooleanField(default=False, verbose_name="Payment suscceded")

    class Meta:
        verbose_name = "Payment"
        verbose_name_plural = "Payments"