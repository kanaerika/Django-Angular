from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Avg, Count
from django.shortcuts import get_object_or_404
from .models import Destination, Hotel, HotelBooking, DestinationReview
from .serializers import (
    DestinationSerializer, DestinationCreateUpdateSerializer,
    HotelSerializer, HotelCreateUpdateSerializer,
    HotelBookingSerializer, HotelBookingCreateSerializer,
    HotelBookingUpdateSerializer, DestinationReviewSerializer,
    DestinationReviewCreateSerializer
)
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdmin


class DestinationViewSet(viewsets.ModelViewSet):
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer
    permission_classes = [IsAdminOrReadOnly]
    
    def get_queryset(self):
        queryset = Destination.objects.all()
        
        # Recherche
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(city__icontains=search) |
                Q(description__icontains=search)
            )
        
        # Trier par note
        order_by_rating = self.request.query_params.get('order_by_rating')
        if order_by_rating == 'desc':
            queryset = queryset.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')
        elif order_by_rating == 'asc':
            queryset = queryset.annotate(avg_rating=Avg('reviews__rating')).order_by('avg_rating')
        
        # Trier par popularité (nombre de réservations d'hôtels)
        order_by_popular = self.request.query_params.get('order_by_popular')
        if order_by_popular == 'desc':
            queryset = queryset.annotate(bookings_count=Count('hotels__bookings')).order_by('-bookings_count')
        
        return queryset.prefetch_related('hotels')
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return DestinationCreateUpdateSerializer
        return DestinationSerializer
    
    @action(detail=True, methods=['get'], url_path='hotels')
    def get_hotels(self, request, pk=None):
        """Récupérer tous les hôtels d'une destination"""
        destination = self.get_object()
        hotels = destination.hotels.all()
        
        serializer = HotelSerializer(hotels, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], url_path='reviews')
    def get_reviews(self, request, pk=None):
        """Récupérer tous les avis d'une destination"""
        destination = self.get_object()
        reviews = destination.reviews.all().order_by('-created_at')
        
        serializer = DestinationReviewSerializer(reviews, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='popular')
    def popular_destinations(self, request):
        """Récupérer les destinations les plus populaires"""
        destinations = Destination.objects.annotate(
            total_bookings=Count('hotels__bookings')
        ).filter(total_bookings__gt=0).order_by('-total_bookings')[:10]
        
        serializer = self.get_serializer(destinations, many=True)
        return Response(serializer.data)


class HotelViewSet(viewsets.ModelViewSet):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    permission_classes = [IsAdminOrReadOnly]
    
    def get_queryset(self):
        queryset = Hotel.objects.all()
        
        # Filtrer par destination
        destination_id = self.request.query_params.get('destination')
        if destination_id:
            queryset = queryset.filter(destination_id=destination_id)
        
        # Recherche
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(address__icontains=search)
            )
        
        return queryset.select_related('destination')
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return HotelCreateUpdateSerializer
        return HotelSerializer
    
    @action(detail=True, methods=['get'], url_path='bookings')
    def get_bookings(self, request, pk=None):
        """Récupérer toutes les réservations d'un hôtel (admin seulement)"""
        if not request.user.is_staff:
            return Response(
                {"detail": "Vous n'êtes pas autorisé à voir ces réservations."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        hotel = self.get_object()
        bookings = hotel.bookings.all().order_by('-created_at')
        
        serializer = HotelBookingSerializer(bookings, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], url_path='available')
    def check_availability(self, request, pk=None):
        """Vérifier la disponibilité d'un hôtel pour des dates données"""
        hotel = self.get_object()
        check_in = request.query_params.get('check_in')
        check_out = request.query_params.get('check_out')
        
        if not check_in or not check_out:
            return Response(
                {"error": "Veuillez fournir check_in et check_out."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Compter les réservations existantes
        bookings = hotel.bookings.filter(
            status__in=['pending', 'confirmed'],
            check_in__lt=check_out,
            check_out__gt=check_in
        ).count()
        
        # Logique simple - à adapter selon vos besoins
        is_available = bookings < 10  # Supposons 10 chambres
        
        return Response({
            "hotel_id": hotel.id,
            "hotel_name": hotel.name,
            "check_in": check_in,
            "check_out": check_out,
            "is_available": is_available
        })


class HotelBookingViewSet(viewsets.ModelViewSet):
    queryset = HotelBooking.objects.all()
    serializer_class = HotelBookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = HotelBooking.objects.all()
        
        # Les utilisateurs normaux voient seulement leurs propres réservations
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        
        # Filtrer par statut
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filtrer par hôtel
        hotel_id = self.request.query_params.get('hotel')
        if hotel_id:
            queryset = queryset.filter(hotel_id=hotel_id)
        
        return queryset.select_related('user', 'hotel', 'hotel__destination')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return HotelBookingCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return HotelBookingUpdateSerializer
        return HotelBookingSerializer
    
    def get_permissions(self):
        if self.action == 'destroy':
            return [permissions.IsAuthenticated(), IsOwnerOrAdmin()]
        return [permissions.IsAuthenticated()]
    
    def perform_create(self, serializer):
        serializer.save()
    
    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel_booking(self, request, pk=None):
        """Annuler une réservation"""
        booking = self.get_object()
        
        # Vérifier les permissions
        if booking.user != request.user and not request.user.is_staff:
            return Response(
                {"detail": "Vous n'êtes pas autorisé à annuler cette réservation."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if booking.status == 'cancelled':
            return Response(
                {"detail": "Cette réservation est déjà annulée."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking.status = 'cancelled'
        booking.save(update_fields=['status'])
        
        return Response({
            "message": "Réservation annulée avec succès.",
            "booking_id": booking.id
        })
    
    @action(detail=False, methods=['get'], url_path='my-bookings')
    def my_bookings(self, request):
        """Récupérer les réservations de l'utilisateur connecté"""
        bookings = HotelBooking.objects.filter(user=request.user).order_by('-created_at')
        
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)


class DestinationReviewViewSet(viewsets.ModelViewSet):
    queryset = DestinationReview.objects.all()
    serializer_class = DestinationReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = DestinationReview.objects.all()
        
        # Filtrer par destination
        destination_id = self.request.query_params.get('destination')
        if destination_id:
            queryset = queryset.filter(destination_id=destination_id)
        
        # Filtrer par utilisateur
        user_id = self.request.query_params.get('user')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        return queryset.select_related('user', 'destination')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DestinationReviewCreateSerializer
        return DestinationReviewSerializer
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsOwnerOrAdmin()]
        return [permissions.IsAuthenticated()]
    
    @action(detail=False, methods=['get'], url_path='my-reviews')
    def my_reviews(self, request):
        """Récupérer les avis de l'utilisateur connecté"""
        reviews = DestinationReview.objects.filter(user=request.user).order_by('-created_at')
        
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)