from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Avg, Count, F
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Category, Activity, ActivityImage, Schedule
from .serializers import (
    CategorySerializer, CategoryCreateUpdateSerializer,
    ActivityListSerializer, ActivityDetailSerializer,
    ActivityCreateUpdateSerializer, ActivityImageSerializer,
    ActivityImageUploadSerializer, ScheduleSerializer,
    ScheduleCreateUpdateSerializer, AvailableScheduleSerializer
)
from .permissions import IsAdminOrReadOnly, IsCreatorOrAdmin


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CategoryCreateUpdateSerializer
        return CategorySerializer
    
    def perform_create(self, serializer):
        from django.utils.text import slugify
        instance = serializer.save()
        instance.slug = slugify(instance.name)
        instance.save(update_fields=['slug'])
    
    @action(detail=True, methods=['get'], url_path='activities')
    def get_activities(self, request, slug=None):
        """Récupérer toutes les activités d'une catégorie"""
        category = self.get_object()
        activities = category.activities.filter(is_active=True)
        
        # Pagination
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 12))
        start = (page - 1) * page_size
        end = start + page_size
        
        serializer = ActivityListSerializer(activities[start:end], many=True, context={'request': request})
        
        return Response({
            'category': category.name,
            'count': activities.count(),
            'page': page,
            'page_size': page_size,
            'results': serializer.data
        })


class ActivityViewSet(viewsets.ModelViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivityListSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    
    def get_queryset(self):
        """Filtrer les activités"""
        queryset = Activity.objects.all()
        
        # Filtrer par statut actif (sauf pour les admins)
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)
        
        # Filtrer par ville
        city_slug = self.request.query_params.get('city')
        if city_slug:
            queryset = queryset.filter(city__slug=city_slug)
        
        # Filtrer par pays
        country_code = self.request.query_params.get('country')
        if country_code:
            queryset = queryset.filter(city__country__iso_code=country_code)
        
        # Filtrer par catégorie
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(categories__slug=category)
        
        # Recherche par titre
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(city__name__icontains=search)
            )
        
        # Filtrer par prix
        min_price = self.request.query_params.get('min_price')
        if min_price:
            queryset = queryset.filter(base_price__gte=min_price)
        
        max_price = self.request.query_params.get('max_price')
        if max_price:
            queryset = queryset.filter(base_price__lte=max_price)
        
        # Filtrer par durée
        min_duration = self.request.query_params.get('min_duration')
        if min_duration:
            queryset = queryset.filter(duration_hours__gte=min_duration)
        
        max_duration = self.request.query_params.get('max_duration')
        if max_duration:
            queryset = queryset.filter(duration_hours__lte=max_duration)
        
        # Trier
        ordering = self.request.query_params.get('ordering', '-created_at')
        if ordering == 'price':
            queryset = queryset.order_by('base_price')
        elif ordering == '-price':
            queryset = queryset.order_by('-base_price')
        elif ordering == 'rating':
            queryset = queryset.order_by('cached_rating')
        elif ordering == '-rating':
            queryset = queryset.order_by('-cached_rating')
        elif ordering == 'duration':
            queryset = queryset.order_by('duration_hours')
        elif ordering == '-duration':
            queryset = queryset.order_by('-duration_hours')
        else:
            queryset = queryset.order_by('-created_at')
        
        # Précharger les relations pour optimiser
        queryset = queryset.select_related('city', 'city__country')
        queryset = queryset.prefetch_related('categories', 'images')
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ActivityDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ActivityCreateUpdateSerializer
        return ActivityListSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsCreatorOrAdmin()]
        return [permissions.IsAuthenticatedOrReadOnly()]
    
    @action(detail=True, methods=['get'], url_path='schedules')
    def get_schedules(self, request, slug=None):
        """Récupérer tous les créneaux d'une activité"""
        activity = self.get_object()
        schedules = activity.schedules.all()
        
        # Filtrer par date
        upcoming_only = request.query_params.get('upcoming', 'true').lower() == 'true'
        if upcoming_only:
            schedules = schedules.filter(date__gte=timezone.now().date())
        
        # Filtrer par disponibilité
        available_only = request.query_params.get('available', 'true').lower() == 'true'
        if available_only:
            schedules = schedules.filter(available_spots__gt=0)
        
        # Trier par date
        schedules = schedules.order_by('date', 'start_time')
        
        serializer = ScheduleSerializer(schedules, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], url_path='available-schedules')
    def get_available_schedules(self, request, slug=None):
        """Récupérer les créneaux disponibles d'une activité"""
        activity = self.get_object()
        today = timezone.now().date()
        
        schedules = activity.schedules.filter(
            date__gte=today,
            available_spots__gt=0
        ).order_by('date', 'start_time')[:30]  # Limiter à 30 créneaux
        
        serializer = AvailableScheduleSerializer(schedules, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='images')
    def upload_image(self, request, slug=None):
        """Uploader une image pour une activité"""
        activity = self.get_object()
        
        # Vérifier les permissions
        if not IsCreatorOrAdmin().has_object_permission(request, self, activity):
            return Response(
                {"detail": "Vous n'êtes pas autorisé à ajouter des images à cette activité."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ActivityImageUploadSerializer(
            data={**request.data, 'activity': activity.id},
            context={'request': request}
        )
        
        if serializer.is_valid():
            image = serializer.save()
            return Response(ActivityImageSerializer(image, context={'request': request}).data, 
                          status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], url_path='featured')
    def featured_activities(self, request):
        """Récupérer les activités en vedette (les mieux notées)"""
        activities = Activity.objects.filter(
            is_active=True,
            cached_rating__gte=4.0
        ).order_by('-cached_rating', '-created_at')[:12]
        
        serializer = self.get_serializer(activities, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='popular')
    def popular_activities(self, request):
        """Récupérer les activités les plus populaires (le plus de réservations)"""
        from booking.models import Booking
        
        activities = Activity.objects.filter(is_active=True).annotate(
            booking_count=Count('schedules__bookings', filter=Q(schedules__bookings__status__in=['confirmed', 'completed']))
        ).filter(booking_count__gt=0).order_by('-booking_count')[:12]
        
        serializer = self.get_serializer(activities, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], url_path='reviews')
    def get_reviews(self, request, slug=None):
        """Récupérer les avis d'une activité"""
        from reviews.models import Review
        from reviews.serializers import ReviewSerializer
        
        activity = self.get_object()
        reviews = Review.objects.filter(activity=activity, is_visible=True).order_by('-created_at')
        
        # Pagination
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        start = (page - 1) * page_size
        end = start + page_size
        
        serializer = ReviewSerializer(reviews[start:end], many=True)
        
        return Response({
            'count': reviews.count(),
            'page': page,
            'page_size': page_size,
            'results': serializer.data
        })


class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = [IsAdminOrReadOnly]
    
    def get_queryset(self):
        queryset = Schedule.objects.all()
        
        # Filtrer par activité
        activity_id = self.request.query_params.get('activity')
        if activity_id:
            queryset = queryset.filter(activity_id=activity_id)
        
        # Filtrer par date
        from_date = self.request.query_params.get('from_date')
        if from_date:
            queryset = queryset.filter(date__gte=from_date)
        
        to_date = self.request.query_params.get('to_date')
        if to_date:
            queryset = queryset.filter(date__lte=to_date)
        
        # Filtrer par disponibilité
        available_only = self.request.query_params.get('available', 'false').lower() == 'true'
        if available_only:
            queryset = queryset.filter(available_spots__gt=0)
        
        # Trier
        queryset = queryset.order_by('date', 'start_time')
        
        return queryset.select_related('activity')
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ScheduleCreateUpdateSerializer
        return ScheduleSerializer


class ActivityImageViewSet(viewsets.ModelViewSet):
    queryset = ActivityImage.objects.all()
    serializer_class = ActivityImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = ActivityImage.objects.all()
        
        # Filtrer par activité
        activity_id = self.request.query_params.get('activity')
        if activity_id:
            queryset = queryset.filter(activity_id=activity_id)
        
        return queryset.select_related('activity')
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
    
    def perform_destroy(self, instance):
        """Supprimer l'image du stockage"""
        if instance.image:
            instance.image.delete(save=False)
        instance.delete()
    
    @action(detail=True, methods=['post'], url_path='set-cover')
    def set_as_cover(self, request, pk=None):
        """Définir cette image comme image de couverture"""
        image = self.get_object()
        
        # Retirer le flag cover des autres images de la même activité
        ActivityImage.objects.filter(activity=image.activity, is_cover=True).update(is_cover=False)
        
        # Définir cette image comme cover
        image.is_cover = True
        image.save(update_fields=['is_cover'])
        
        return Response({"message": "Image définie comme couverture."})