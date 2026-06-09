from rest_framework import serializers
from .models import Review
from tour.models import Activity
from account.serializers import UserSerializer

class ReviewSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    activity_title = serializers.CharField(source='activity.title', read_only=True)
    activity_slug = serializers.CharField(source='activity.slug', read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id', 'user', 'user_username', 'user_full_name',
            'activity', 'activity_title', 'activity_slug',
            'rating', 'title', 'comment', 'is_visible',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'user']


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['activity', 'rating', 'title', 'comment']
    
    def validate_activity(self, value):
        """Vérifier que l'activité existe et est active"""
        if not value.is_active:
            raise serializers.ValidationError("Cette activité n'est pas disponible pour les avis.")
        return value
    
    def validate(self, attrs):
        """Vérifier que l'utilisateur n'a pas déjà laissé un avis sur cette activité"""
        user = self.context['request'].user
        activity = attrs['activity']
        
        if Review.objects.filter(user=user, activity=activity).exists():
            raise serializers.ValidationError(
                "Vous avez déjà laissé un avis pour cette activité."
            )
        return attrs
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ReviewUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['rating', 'title', 'comment']
    
    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("La note doit être comprise entre 1 et 5.")
        return value


class ReviewModerateSerializer(serializers.ModelSerializer):
    """Serializer pour la modération des avis (admin seulement)"""
    class Meta:
        model = Review
        fields = ['is_visible']


class ActivityRatingSerializer(serializers.Serializer):
    """Serializer pour les statistiques de notation d'une activité"""
    average_rating = serializers.FloatField()
    total_reviews = serializers.IntegerField()
    rating_distribution = serializers.DictField()
    rating_1 = serializers.IntegerField()
    rating_2 = serializers.IntegerField()
    rating_3 = serializers.IntegerField()
    rating_4 = serializers.IntegerField()
    rating_5 = serializers.IntegerField()