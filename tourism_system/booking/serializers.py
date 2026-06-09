from rest_framework import serializers
from .models import Booking, Payment
from tour.models import Schedule, Activity
from account.serializers import UserSerializer
from django.utils import timezone

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'booking', 'method', 'stripe_payment_intent_id',
            'amount_paid', 'is_successful', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'amount_paid']


class BookingSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    activity_title = serializers.CharField(source='schedule.activity.title', read_only=True)
    activity_slug = serializers.CharField(source='schedule.activity.slug', read_only=True)
    city_name = serializers.CharField(source='schedule.activity.city.name', read_only=True)
    schedule_date = serializers.DateField(source='schedule.date', read_only=True)
    schedule_start_time = serializers.TimeField(source='schedule.start_time', read_only=True)
    payment = PaymentSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'id', 'booking_reference', 'user', 'user_username', 'user_full_name',
            'schedule', 'activity_title', 'activity_slug', 'city_name',
            'schedule_date', 'schedule_start_time', 'number_of_travelers',
            'total_price', 'status', 'status_display', 'special_requests',
            'payment', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'booking_reference', 'total_price', 'created_at', 'updated_at'
        ]


class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['schedule', 'number_of_travelers', 'special_requests']
    
    def validate_schedule(self, value):
        """Vérifier que le créneau est valide et a des places disponibles"""
        # Vérifier que la date n'est pas passée
        if value.date < timezone.now().date():
            raise serializers.ValidationError("Cette date est déjà passée.")
        
        # Vérifier que l'activité est active
        if not value.activity.is_active:
            raise serializers.ValidationError("Cette activité n'est plus disponible.")
        
        # Vérifier les places disponibles
        if value.available_spots <= 0:
            raise serializers.ValidationError("Il n'y a plus de places disponibles pour ce créneau.")
        
        return value
    
    def validate_number_of_travelers(self, value):
        """Vérifier que le nombre de voyageurs est valide"""
        if value <= 0:
            raise serializers.ValidationError("Le nombre de voyageurs doit être supérieur à 0.")
        
        if value > 20:
            raise serializers.ValidationError("Le nombre maximum de voyageurs par réservation est de 20.")
        
        return value
    
    def validate(self, attrs):
        """Vérifier les places disponibles par rapport au nombre de voyageurs"""
        schedule = attrs['schedule']
        number_of_travelers = attrs['number_of_travelers']
        
        if number_of_travelers > schedule.available_spots:
            raise serializers.ValidationError({
                "number_of_travelers": f"Il ne reste que {schedule.available_spots} places disponibles."
            })
        
        return attrs
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        booking = super().create(validated_data)
        
        # Réduire les places disponibles
        schedule = booking.schedule
        schedule.available_spots -= booking.number_of_travelers
        schedule.save(update_fields=['available_spots'])
        
        return booking


class BookingUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['special_requests']


class BookingStatusUpdateSerializer(serializers.Serializer):
    """Serializer pour mettre à jour le statut d'une réservation"""
    status = serializers.ChoiceField(choices=Booking.STATUS_CHOICES)
    
    def validate_status(self, value):
        # Vérifier la transition de statut valide
        old_status = self.instance.status if self.instance else None
        
        if old_status == 'cancelled' and value != 'cancelled':
            raise serializers.ValidationError("Une réservation annulée ne peut pas être modifiée.")
        
        if old_status == 'refunded' and value != 'refunded':
            raise serializers.ValidationError("Une réservation remboursée ne peut pas être modifiée.")
        
        if old_status == 'completed' and value != 'completed':
            raise serializers.ValidationError("Une réservation terminée ne peut pas être modifiée.")
        
        return value


class PaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['method', 'stripe_payment_intent_id']
    
    def validate(self, attrs):
        booking = self.context['booking']
        
        # Vérifier que la réservation est en attente de paiement
        if booking.status != 'pending':
            raise serializers.ValidationError(
                "Cette réservation ne peut pas être payée car son statut est '{}'.".format(booking.status)
            )
        
        # Vérifier que la réservation n'a pas déjà un paiement
        if hasattr(booking, 'payment') and booking.payment:
            raise serializers.ValidationError("Cette réservation a déjà un paiement associé.")
        
        return attrs
    
    def create(self, validated_data):
        booking = self.context['booking']
        validated_data['booking'] = booking
        validated_data['amount_paid'] = booking.total_price
        return super().create(validated_data)


class BookingCancelSerializer(serializers.Serializer):
    """Serializer pour annuler une réservation"""
    reason = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, attrs):
        booking = self.instance
        
        # Vérifier que la réservation peut être annulée
        if booking.status in ['cancelled', 'refunded', 'completed']:
            raise serializers.ValidationError(
                f"Cette réservation ne peut pas être annulée car elle est déjà '{booking.get_status_display()}'."
            )
        
        return attrs


class UserBookingStatsSerializer(serializers.Serializer):
    """Serializer pour les statistiques de réservation d'un utilisateur"""
    total_bookings = serializers.IntegerField()
    pending_bookings = serializers.IntegerField()
    confirmed_bookings = serializers.IntegerField()
    completed_bookings = serializers.IntegerField()
    cancelled_bookings = serializers.IntegerField()
    total_spent = serializers.DecimalField(max_digits=10, decimal_places=2)