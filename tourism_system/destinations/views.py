from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from django.db.models import Q, Count, Avg
from django.shortcuts import get_object_or_404
from .models import Country, City
from .serializers import (
    CountrySerializer, CountryCreateUpdateSerializer, CountryDetailSerializer,
    CitySerializer, CityCreateUpdateSerializer, CityDetailSerializer,
    CityWithActivitiesSerializer
)
from .permissions import IsAdminOrReadOnly


class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [IsAdminOrReadOnly]
    
    def get_queryset(self):
        """Filtrer les pays"""
        queryset = Country.objects.all()
        
        # Recherche par nom
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(iso_code__icontains=search)
            )
        
        # Trier par nombre d'activités
        order_by_activities = self.request.query_params.get('order_by_activities')
        if order_by_activities == 'asc':
            queryset = queryset.annotate(
                total_activities=Count('cities__activities')
            ).order_by('total_activities')
        elif order_by_activities == 'desc':
            queryset = queryset.annotate(
                total_activities=Count('cities__activities')
            ).order_by('-total_activities')
        
        return queryset.prefetch_related('cities')
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CountryCreateUpdateSerializer
        elif self.action == 'retrieve':
            return CountryDetailSerializer
        return CountrySerializer
    
    @action(detail=True, methods=['get'], url_path='cities')
    def get_cities(self, request, pk=None):
        """Récupérer toutes les villes d'un pays"""
        country = self.get_object()
        cities = country.cities.all()
        
        # Filtrer par recherche
        search = request.query_params.get('search')
        if search:
            cities = cities.filter(name__icontains=search)
        
        # Pagination
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        start = (page - 1) * page_size
        end = start + page_size
        
        serializer = CitySerializer(cities[start:end], many=True, context={'request': request})
        
        return Response({
            'count': cities.count(),
            'page': page,
            'page_size': page_size,
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'], url_path='popular')
    def popular_countries(self, request):
        """Récupérer les pays les plus populaires (avec le plus d'activités)"""
        countries = Country.objects.annotate(
            total_activities=Count('cities__activities')
        ).filter(total_activities__gt=0).order_by('-total_activities')[:10]
        
        serializer = self.get_serializer(countries, many=True)
        return Response(serializer.data)


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [IsAdminOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CityCreateUpdateSerializer  # Sera affiché dans le formulaire
        return CitySerializer
    
    def get_queryset(self):
        """Filtrer les villes"""
        queryset = City.objects.all()
        
        # Filtrer par pays
        country_id = self.request.query_params.get('country')
        if country_id:
            queryset = queryset.filter(country_id=country_id)
        
        # Recherche par nom
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        # Trier par nombre d'activités
        order_by_activities = self.request.query_params.get('order_by_activities')
        if order_by_activities == 'asc':
            queryset = queryset.annotate(
                total_activities=Count('activities')
            ).order_by('total_activities')
        elif order_by_activities == 'desc':
            queryset = queryset.annotate(
                total_activities=Count('activities')
            ).order_by('-total_activities')
        
        # Trier par note moyenne
        order_by_rating = self.request.query_params.get('order_by_rating')
        if order_by_rating == 'asc':
            queryset = queryset.annotate(
                avg_rating=Avg('activities__cached_rating')
            ).order_by('avg_rating')
        elif order_by_rating == 'desc':
            queryset = queryset.annotate(
                avg_rating=Avg('activities__cached_rating')
            ).order_by('-avg_rating')
        
        return queryset.select_related('country')
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CityCreateUpdateSerializer
        elif self.action == 'retrieve':
            # Utiliser un serializer différent selon les paramètres
            if self.request.query_params.get('include_activities') == 'true':
                return CityWithActivitiesSerializer
            return CityDetailSerializer
        return CitySerializer
    
    def perform_create(self, serializer):
        """Créer automatiquement le slug à partir du nom"""
        instance = serializer.save()
        from django.utils.text import slugify
        instance.slug = slugify(f"{instance.name}-{instance.country.iso_code}")
        instance.save(update_fields=['slug'])
    
    def perform_update(self, serializer):
        """Mettre à jour le slug si le nom change"""
        instance = serializer.save()
        if 'name' in serializer.validated_data:
            from django.utils.text import slugify
            instance.slug = slugify(f"{instance.name}-{instance.country.iso_code}")
            instance.save(update_fields=['slug'])
    
    @action(detail=True, methods=['get'], url_path='activities')
    def get_activities(self, request, pk=None):
        """Récupérer toutes les activités d'une ville"""
        city = self.get_object()
        
        from tour.serializers import ActivityListSerializer
        from tour.models import Activity
        
        activities = Activity.objects.filter(city=city, is_active=True)
        
        # Filtrer par catégorie
        category = request.query_params.get('category')
        if category:
            activities = activities.filter(categories__slug=category)
        
        # Filtrer par prix
        min_price = request.query_params.get('min_price')
        if min_price:
            activities = activities.filter(base_price__gte=min_price)
        
        max_price = request.query_params.get('max_price')
        if max_price:
            activities = activities.filter(base_price__lte=max_price)
        
        # Filtrer par durée
        min_duration = request.query_params.get('min_duration')
        if min_duration:
            activities = activities.filter(duration_hours__gte=min_duration)
        
        max_duration = request.query_params.get('max_duration')
        if max_duration:
            activities = activities.filter(duration_hours__lte=max_duration)
        
        # Trier
        ordering = request.query_params.get('ordering', '-created_at')
        if ordering in ['price', '-price', 'rating', '-rating', 'duration', '-duration']:
            if ordering == 'price':
                activities = activities.order_by('base_price')
            elif ordering == '-price':
                activities = activities.order_by('-base_price')
            elif ordering == 'rating':
                activities = activities.order_by('cached_rating')
            elif ordering == '-rating':
                activities = activities.order_by('-cached_rating')
            elif ordering == 'duration':
                activities = activities.order_by('duration_hours')
            elif ordering == '-duration':
                activities = activities.order_by('-duration_hours')
        else:
            activities = activities.order_by('-created_at')
        
        # Pagination
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        start = (page - 1) * page_size
        end = start + page_size
        
        serializer = ActivityListSerializer(activities[start:end], many=True, context={'request': request})
        
        return Response({
            'count': activities.count(),
            'page': page,
            'page_size': page_size,
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'], url_path='search')
    def search_cities(self, request):
        """Rechercher des villes"""
        query = request.query_params.get('q', '')
        if not query or len(query) < 2:
            return Response({
                'results': []
            })
        
        cities = City.objects.filter(
            Q(name__icontains=query) |
            Q(country__name__icontains=query) |
            Q(description__icontains=query)
        ).select_related('country')[:20]
        
        serializer = self.get_serializer(cities, many=True)
        return Response({
            'query': query,
            'count': cities.count(),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'], url_path='featured')
    def featured_cities(self, request):
        """Récupérer les villes en vedette (avec le plus d'activités)"""
        cities = City.objects.annotate(
            total_activities=Count('activities')
        ).filter(total_activities__gt=0).order_by('-total_activities')[:12]
        
        serializer = self.get_serializer(cities, many=True)
        return Response(serializer.data)