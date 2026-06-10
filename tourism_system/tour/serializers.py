from django.utils import timezone
from rest_framework import serializers
from .models import Category, Activity, ActivityImage, Schedule
from destinations.serializers import CitySerializer
from account.serializers import UserSerializer

class CategorySerializer(serializers.ModelSerializer):
    activities_count = serializers.IntegerField(source='activities.count', read_only=True)
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'activities_count']
        read_only_fields = ['slug']


class CategoryCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name']


class ActivityImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ActivityImage
        fields = ['id', 'activity', 'image', 'image_url', 'is_cover', 'order']
        read_only_fields = ['id']
    
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url if obj.image else None


class ScheduleSerializer(serializers.ModelSerializer):
    activity_title = serializers.CharField(source='activity.title', read_only=True)
    available_spots_original = serializers.IntegerField(source='activity.max_travelers', read_only=True)
    actual_price = serializers.DecimalField(source='get_actual_price', read_only=True, max_digits=10, decimal_places=2)
    is_full = serializers.SerializerMethodField()
    
    class Meta:
        model = Schedule
        fields = [
            'id', 'activity', 'activity_title', 'date', 'start_time',
            'available_spots', 'available_spots_original', 'actual_price',
            'price_override', 'is_full', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_is_full(self, obj):
        return obj.available_spots <= 0


class ScheduleCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ['activity', 'date', 'start_time', 'available_spots', 'price_override']
    
    def validate(self, attrs):
        activity = attrs.get('activity')
        available_spots = attrs.get('available_spots', 0)
        
        if activity and available_spots > activity.max_travelers:
            raise serializers.ValidationError({
                "available_spots": f"Les places disponibles ne peuvent pas dépasser {activity.max_travelers} (max voyageurs de l'activité)."
            })
        
        return attrs


class ActivityListSerializer(serializers.ModelSerializer):
    """Serializer pour la liste des activités (aperçu)"""
    city_name = serializers.CharField(source='city.name', read_only=True)
    city_slug = serializers.CharField(source='city.slug', read_only=True)
    country_name = serializers.CharField(source='city.country.name', read_only=True)
    cover_image = serializers.SerializerMethodField()
    average_rating = serializers.FloatField(source='cached_rating', read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    
    class Meta:
        model = Activity
        fields = [
            'id', 'title', 'slug', 'city', 'city_name', 'city_slug',
            'country_name', 'base_price', 'duration_hours', 'cached_rating',
            'average_rating', 'categories', 'cover_image', 'created_at'
        ]
    
    def get_cover_image(self, obj):
        cover = obj.images.filter(is_cover=True).first()
        if cover:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(cover.image.url)
            return cover.image.url
        return None


class ActivityDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour une activité"""
    city = CitySerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    images = ActivityImageSerializer(many=True, read_only=True)
    schedules = ScheduleSerializer(many=True, read_only=True)
    average_rating = serializers.FloatField(source='cached_rating', read_only=True)
    reviews_count = serializers.SerializerMethodField()
    lowest_price = serializers.SerializerMethodField()
    
    class Meta:
        model = Activity
        fields = [
            'id', 'title', 'slug', 'city', 'description', 'what_to_bring',
            'base_price', 'lowest_price', 'max_travelers', 'duration_hours',
            'is_active', 'cached_rating', 'average_rating', 'reviews_count',
            'categories', 'images', 'schedules', 'created_by',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'cached_rating']
    
    def get_reviews_count(self, obj):
        from reviews.models import Review
        return Review.objects.filter(activity=obj, is_visible=True).count()
    
    def get_lowest_price(self, obj):
        """Retourner le prix le plus bas parmi les créneaux disponibles"""
        upcoming_schedules = obj.schedules.filter(
            date__gte=timezone.now().date(),
            available_spots__gt=0
        )
        
        if upcoming_schedules.exists():
            prices = [s.get_actual_price() for s in upcoming_schedules]
            return min(prices)
        
        return obj.base_price


class ActivityCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour la création/mise à jour d'une activité"""
    categories = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Category.objects.all(), required=False
    )
    
    class Meta:
        model = Activity
        fields = [
            'title', 'city', 'categories', 'description', 'what_to_bring',
            'base_price', 'max_travelers', 'duration_hours', 'is_active'
        ]
    
    def validate_base_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Le prix doit être supérieur à 0.")
        return value
    
    def validate_duration_hours(self, value):
        if value <= 0:
            raise serializers.ValidationError("La durée doit être supérieure à 0.")
        if value > 72:
            raise serializers.ValidationError("La durée ne peut pas dépasser 72 heures.")
        return value
    
    def create(self, validated_data):
        categories = validated_data.pop('categories', [])
        validated_data['created_by'] = self.context['request'].user
        
        # Générer le slug
        from django.utils.text import slugify
        title = validated_data.get('title')
        base_slug = slugify(title)
        
        # Vérifier l'unicité du slug
        from core.utils import generate_unique_slug
        activity = Activity(**validated_data)
        activity.slug = generate_unique_slug(activity, 'title')
        activity.save()
        
        # Ajouter les catégories
        activity.categories.set(categories)
        
        return activity
    
    def update(self, instance, validated_data):
        categories = validated_data.pop('categories', None)
        
        # Mettre à jour les champs
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Mettre à jour le slug si le titre change
        if 'title' in validated_data:
            from django.utils.text import slugify
            from core.utils import generate_unique_slug
            instance.slug = generate_unique_slug(instance, 'title')
        
        instance.save()
        
        # Mettre à jour les catégories
        if categories is not None:
            instance.categories.set(categories)
        
        return instance


class ActivityImageUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityImage
        fields = ['activity', 'image', 'is_cover', 'order']
    
    def validate(self, attrs):
        activity = attrs.get('activity')
        
        # Si cette image est définie comme cover, retirer le flag des autres images
        if attrs.get('is_cover'):
            ActivityImage.objects.filter(activity=activity, is_cover=True).update(is_cover=False)
        
        return attrs


class AvailableScheduleSerializer(serializers.ModelSerializer):
    """Serializer pour les créneaux disponibles d'une activité"""
    activity_title = serializers.CharField(source='activity.title', read_only=True)
    actual_price = serializers.DecimalField(source='get_actual_price', read_only=True, max_digits=10, decimal_places=2)
    formatted_date = serializers.SerializerMethodField()
    formatted_time = serializers.SerializerMethodField()
    
    class Meta:
        model = Schedule
        fields = [
            'id', 'activity', 'activity_title', 'date', 'start_time',
            'formatted_date', 'formatted_time', 'available_spots',
            'actual_price', 'price_override'
        ]
    
    def get_formatted_date(self, obj):
        return obj.date.strftime('%d %B %Y')
    
    def get_formatted_time(self, obj):
        return obj.start_time.strftime('%H:%M')