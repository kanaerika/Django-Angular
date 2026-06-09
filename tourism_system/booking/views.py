from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Booking, Payment
from tour.models import Schedule
from .serializers import (
    BookingSerializer, BookingCreateSerializer, BookingUpdateSerializer,
    BookingStatusUpdateSerializer, PaymentSerializer, PaymentCreateSerializer,
    BookingCancelSerializer, UserBookingStatsSerializer
)
from .permissions import IsBookingOwnerOrAdmin, IsAdminOrReadOnly


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtrer les réservations"""
        queryset = Booking.objects.all()
        
        # Si l'utilisateur n'est pas admin, ne voir que ses propres réservations
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        
        # Filtrer par statut
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filtrer par activité
        activity_id = self.request.query_params.get('activity')
        if activity_id:
            queryset = queryset.filter(schedule__activity_id=activity_id)
        
        # Filtrer par date
        from_date = self.request.query_params.get('from_date')
        if from_date:
            queryset = queryset.filter(schedule__date__gte=from_date)
        
        to_date = self.request.query_params.get('to_date')
        if to_date:
            queryset = queryset.filter(schedule__date__lte=to_date)
        
        # Ordonner par date de création (plus récent d'abord)
        queryset = queryset.order_by('-created_at')
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'create':
            return BookingCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return BookingUpdateSerializer
        elif self.action == 'update_status':
            return BookingStatusUpdateSerializer
        elif self.action == 'cancel':
            return BookingCancelSerializer
        return BookingSerializer
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy', 'cancel']:
            return [permissions.IsAuthenticated(), IsBookingOwnerOrAdmin()]
        elif self.action == 'update_status':
            return [permissions.IsAuthenticated(), permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]
    
    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        """Annuler une réservation"""
        booking = self.get_object()
        serializer = self.get_serializer(booking, data=request.data)
        
        if serializer.is_valid():
            old_status = booking.status
            booking.status = 'cancelled'
            booking.save(update_fields=['status'])
            
            # Remettre les places disponibles
            schedule = booking.schedule
            schedule.available_spots += booking.number_of_travelers
            schedule.save(update_fields=['available_spots'])
            
            # Si un paiement existe, le marquer comme non réussi (remboursement à gérer séparément)
            if hasattr(booking, 'payment') and booking.payment:
                booking.payment.is_successful = False
                booking.payment.save(update_fields=['is_successful'])
            
            return Response({
                "message": "Réservation annulée avec succès.",
                "booking_reference": str(booking.booking_reference),
                "old_status": old_status,
                "new_status": booking.status
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['put', 'patch'], url_path='status')
    def update_status(self, request, pk=None):
        """Mettre à jour le statut d'une réservation (admin seulement)"""
        booking = self.get_object()
        serializer = self.get_serializer(booking, data=request.data)
        
        if serializer.is_valid():
            old_status = booking.status
            booking.status = serializer.validated_data['status']
            booking.save(update_fields=['status'])
            
            # Si la réservation est terminée, permettre à l'utilisateur de laisser un avis
            if booking.status == 'completed' and old_status != 'completed':
                # Notification à implémenter plus tard
                pass
            
            return Response({
                "message": "Statut mis à jour avec succès.",
                "booking_reference": str(booking.booking_reference),
                "old_status": old_status,
                "new_status": booking.status
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], url_path='pay')
    def create_payment(self, request, pk=None):
        """Créer un paiement pour une réservation"""
        booking = self.get_object()
        
        # Vérifier que l'utilisateur est le propriétaire
        if booking.user != request.user and not request.user.is_staff:
            return Response(
                {"detail": "Vous n'êtes pas autorisé à payer cette réservation."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = PaymentCreateSerializer(
            data=request.data,
            context={'booking': booking}
        )
        
        if serializer.is_valid():
            payment = serializer.save()
            
            # Si le paiement est réussi, mettre à jour le statut de la réservation
            if payment.is_successful:
                booking.status = 'confirmed'
                booking.save(update_fields=['status'])
            
            return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], url_path='my-stats')
    def my_stats(self, request):
        """Obtenir les statistiques de réservation de l'utilisateur connecté"""
        bookings = Booking.objects.filter(user=request.user)
        
        stats = {
            'total_bookings': bookings.count(),
            'pending_bookings': bookings.filter(status='pending').count(),
            'confirmed_bookings': bookings.filter(status='confirmed').count(),
            'completed_bookings': bookings.filter(status='completed').count(),
            'cancelled_bookings': bookings.filter(status='cancelled').count(),
            'total_spent': bookings.filter(status__in=['confirmed', 'completed']).aggregate(
                total=Sum('total_price')
            )['total'] or 0,
        }
        
        serializer = UserBookingStatsSerializer(stats)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='upcoming')
    def upcoming_bookings(self, request):
        """Récupérer les réservations à venir"""
        today = timezone.now().date()
        bookings = Booking.objects.filter(
            user=request.user,
            schedule__date__gte=today,
            status__in=['confirmed', 'pending']
        ).order_by('schedule__date', 'schedule__start_time')
        
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='past')
    def past_bookings(self, request):
        """Récupérer les réservations passées"""
        today = timezone.now().date()
        bookings = Booking.objects.filter(
            user=request.user,
            schedule__date__lt=today
        ).order_by('-schedule__date')
        
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='available-spots/(?P<schedule_id>[^/.]+)')
    def check_available_spots(self, request, schedule_id=None):
        """Vérifier les places disponibles pour un créneau"""
        schedule = get_object_or_404(Schedule, id=schedule_id)
        
        return Response({
            "schedule_id": schedule.id,
            "activity_title": schedule.activity.title,
            "date": schedule.date,
            "start_time": schedule.start_time,
            "available_spots": schedule.available_spots,
            "max_travelers": schedule.activity.max_travelers,
            "price_per_person": schedule.get_actual_price()
        })


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet en lecture seule pour les paiements"""
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Payment.objects.all()
        
        # Si l'utilisateur n'est pas admin, ne voir que ses propres paiements
        if not self.request.user.is_staff:
            queryset = queryset.filter(booking__user=self.request.user)
        
        return queryset.select_related('booking')