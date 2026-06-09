from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from django.db.models import Avg, Count, Q
from django.utils import timezone
from .models import Review
from tour.models import Activity
from .serializers import (
    ReviewSerializer, ReviewCreateSerializer, ReviewUpdateSerializer,
    ReviewModerateSerializer, ActivityRatingSerializer
)
from .permissions import IsOwnerOrAdmin, IsAdminOrReadOnly


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtrer les avis"""
        queryset = Review.objects.all()
        
        # Filtrer par activité
        activity_id = self.request.query_params.get('activity')
        if activity_id:
            queryset = queryset.filter(activity_id=activity_id)
        
        # Filtrer par utilisateur
        user_id = self.request.query_params.get('user')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Filtrer par note
        rating = self.request.query_params.get('rating')
        if rating:
            queryset = queryset.filter(rating=rating)
        
        # Filtrer par visibilité
        show_all = self.request.query_params.get('show_all', False)
        if show_all == 'true' and self.request.user.is_staff:
            # Les admins peuvent voir tous les avis
            pass
        else:
            # Les utilisateurs normaux voient seulement les avis visibles
            queryset = queryset.filter(is_visible=True)
        
        # Ordonner par date (plus récent d'abord)
        queryset = queryset.order_by('-created_at')
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ReviewCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ReviewUpdateSerializer
        elif self.action == 'moderate':
            return ReviewModerateSerializer
        return ReviewSerializer
    
    def get_permissions(self):
        if self.action == 'destroy':
            return [permissions.IsAuthenticated(), IsOwnerOrAdmin()]
        elif self.action == 'moderate':
            return [permissions.IsAuthenticated(), permissions.IsAdminUser()]
        elif self.action in ['update', 'partial_update']:
            return [permissions.IsAuthenticated(), IsOwnerOrAdmin()]
        return [permissions.IsAuthenticated()]
    
    @action(detail=True, methods=['put', 'patch'], url_path='moderate')
    def moderate(self, request, pk=None):
        """Modérer un avis (admin seulement)"""
        review = self.get_object()
        serializer = self.get_serializer(review, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            
            # Mettre à jour le cache de notation de l'activité
            self._update_activity_rating_cache(review.activity)
            
            return Response(ReviewSerializer(review).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def perform_create(self, serializer):
        review = serializer.save()
        # Mettre à jour le cache de notation après création
        self._update_activity_rating_cache(review.activity)
    
    def perform_update(self, serializer):
        review = serializer.save()
        # Mettre à jour le cache de notation après modification
        self._update_activity_rating_cache(review.activity)
    
    def perform_destroy(self, instance):
        activity = instance.activity
        instance.delete()
        # Mettre à jour le cache de notation après suppression
        self._update_activity_rating_cache(activity)
    
    def _update_activity_rating_cache(self, activity):
        """Mettre à jour la note moyenne en cache de l'activité"""
        from django.db.models import Avg
        
        avg_rating = Review.objects.filter(
            activity=activity, 
            is_visible=True
        ).aggregate(avg=Avg('rating'))['avg']
        
        activity.cached_rating = avg_rating if avg_rating else 0.0
        activity.save(update_fields=['cached_rating'])
    
    @action(detail=False, methods=['get'], url_path='my-reviews')
    def my_reviews(self, request):
        """Récupérer les avis de l'utilisateur connecté"""
        reviews = Review.objects.filter(user=request.user, is_visible=True)
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='activity/(?P<activity_slug>[^/.]+)/ratings')
    def activity_ratings(self, request, activity_slug=None):
        """Obtenir les statistiques de notation pour une activité"""
        activity = get_object_or_404(Activity, slug=activity_slug, is_active=True)
        
        # Récupérer tous les avis visibles pour cette activité
        reviews = Review.objects.filter(activity=activity, is_visible=True)
        
        # Calculer les statistiques
        total_reviews = reviews.count()
        average_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0.0
        
        # Distribution des notes
        rating_distribution = {}
        for i in range(1, 6):
            count = reviews.filter(rating=i).count()
            rating_distribution[str(i)] = count
        
        data = {
            'average_rating': round(average_rating, 2),
            'total_reviews': total_reviews,
            'rating_distribution': rating_distribution,
            'rating_1': rating_distribution.get('1', 0),
            'rating_2': rating_distribution.get('2', 0),
            'rating_3': rating_distribution.get('3', 0),
            'rating_4': rating_distribution.get('4', 0),
            'rating_5': rating_distribution.get('5', 0),
        }
        
        serializer = ActivityRatingSerializer(data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='pending')
    def pending_reviews(self, request):
        """Récupérer les avis en attente de modération (admin seulement)"""
        if not request.user.is_staff:
            return Response(
                {"detail": "Vous n'avez pas la permission d'accéder à cette ressource."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        pending_reviews = Review.objects.filter(is_visible=False)
        serializer = self.get_serializer(pending_reviews, many=True)
        return Response(serializer.data)