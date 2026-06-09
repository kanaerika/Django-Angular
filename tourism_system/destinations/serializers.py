from rest_framework import serializers
from .models import Country, City
from tour.models import Activity

class CountrySerializer(serializers.ModelSerializer):
    cities_count = serializers.IntegerField(source='cities.count', read_only=True)
    activities_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Country
        fields = [
            'id', 'name', 'iso_code', 'cities_count', 'activities_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_activities_count(self, obj):
        """Compter le nombre total d'activités dans ce pays"""
        return Activity.objects.filter(city__country=obj, is_active=True).count()


class CountryCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['name', 'iso_code']


class CitySerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source='country.name', read_only=True)
    country_iso_code = serializers.CharField(source='country.iso_code', read_only=True)
    activities_count = serializers.IntegerField(source='activities.count', read_only=True)
    active_activities_count = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    
    class Meta:
        model = City
        fields = [
            'id', 'name', 'slug', 'country', 'country_name', 'country_iso_code',
            'description', 'thumbnail', 'thumbnail_url', 'latitude', 'longitude',
            'activities_count', 'active_activities_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']
    
    def get_active_activities_count(self, obj):
        """Compter le nombre d'activités actives dans cette ville"""
        return obj.activities.filter(is_active=True).count()
    
    def get_thumbnail_url(self, obj):
        """Retourner l'URL complète de l'image"""
        if obj.thumbnail:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.thumbnail.url)
            return obj.thumbnail.url
        return None


class CityCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['name', 'country', 'description', 'thumbnail', 'latitude', 'longitude']
    
    def validate_slug(self, value):
        """Vérifier que le slug est unique"""
        if City.objects.filter(slug=value).exists():
            raise serializers.ValidationError("Ce slug est déjà utilisé.")
        return value


class CityDetailSerializer(CitySerializer):
    """Serializer détaillé pour une ville avec activités populaires"""
    popular_activities = serializers.SerializerMethodField()
    
    class Meta(CitySerializer.Meta):
        fields = CitySerializer.Meta.fields + ['popular_activities']
    
    def get_popular_activities(self, obj):
        """Récupérer les 5 activités les plus populaires de la ville"""
        from tour.serializers import ActivityListSerializer
        
        popular_activities = obj.activities.filter(
            is_active=True
        ).order_by('-cached_rating', '-created_at')[:5]
        
        return ActivityListSerializer(popular_activities, many=True, context=self.context).data


class CityWithActivitiesSerializer(CitySerializer):
    """Serializer pour une ville avec toutes ses activités"""
    activities = serializers.SerializerMethodField()
    
    class Meta(CitySerializer.Meta):
        fields = CitySerializer.Meta.fields + ['activities']
    
    def get_activities(self, obj):
        from tour.serializers import ActivityListSerializer
        
        activities = obj.activities.filter(is_active=True)
        
        # Filtrer par catégorie si spécifié
        category = self.context.get('category')
        if category:
            activities = activities.filter(categories__slug=category)
        
        return ActivityListSerializer(activities, many=True, context=self.context).data


class CountryDetailSerializer(CountrySerializer):
    """Serializer détaillé pour un pays avec ses villes"""
    cities = CitySerializer(many=True, read_only=True)
    
    class Meta(CountrySerializer.Meta):
        fields = CountrySerializer.Meta.fields + ['cities']