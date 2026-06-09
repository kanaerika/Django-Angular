from rest_framework import serializers
from .models import Destination, Hotel, HotelBooking, DestinationReview

class DestinationSerializer(serializers.ModelSerializer):
    hotels_count = serializers.IntegerField(source='hotels.count', read_only=True)
    reviews_count = serializers.IntegerField(source='reviews.count', read_only=True)
    average_rating = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Destination
        fields = [
            'id', 'name', 'city', 'description', 'image', 'image_url',
            'hotels_count', 'reviews_count', 'average_rating', 'created_at'
        ]
        read_only_fields = ['created_at']
    
    def get_average_rating(self, obj):
        avg = obj.reviews.aggregate(models.Avg('rating'))['rating__avg']
        return round(avg, 2) if avg else 0
    
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class DestinationCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destination
        fields = ['name', 'city', 'description', 'image']


class HotelSerializer(serializers.ModelSerializer):
    destination_name = serializers.CharField(source='destination.name', read_only=True)
    bookings_count = serializers.IntegerField(source='bookings.count', read_only=True)
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Hotel
        fields = [
            'id', 'name', 'address', 'image', 'image_url',
            'destination', 'destination_name', 'bookings_count'
        ]
    
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class HotelCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = ['name', 'address', 'image', 'destination']


class HotelBookingSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    hotel_name = serializers.CharField(source='hotel.name', read_only=True)
    destination_name = serializers.CharField(source='hotel.destination.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    nights = serializers.SerializerMethodField()
    
    class Meta:
        model = HotelBooking
        fields = [
            'id', 'user', 'user_username', 'hotel', 'hotel_name',
            'destination_name', 'check_in', 'check_out', 'nights',
            'guests', 'status', 'status_display', 'created_at'
        ]
        read_only_fields = ['created_at']
    
    def get_nights(self, obj):
        return (obj.check_out - obj.check_in).days


class HotelBookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = HotelBooking
        fields = ['hotel', 'check_in', 'check_out', 'guests']
    
    def validate(self, attrs):
        check_in = attrs['check_in']
        check_out = attrs['check_out']
        
        if check_in >= check_out:
            raise serializers.ValidationError("La date de départ doit être postérieure à la date d'arrivée.")
        
        if check_in < timezone.now().date():
            raise serializers.ValidationError("La date d'arrivée ne peut pas être dans le passé.")
        
        return attrs
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class HotelBookingUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = HotelBooking
        fields = ['status']


class DestinationReviewSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    destination_name = serializers.CharField(source='destination.name', read_only=True)
    
    class Meta:
        model = DestinationReview
        fields = [
            'id', 'user', 'user_username', 'destination', 'destination_name',
            'rating', 'comment', 'created_at'
        ]
        read_only_fields = ['created_at']


class DestinationReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DestinationReview
        fields = ['destination', 'rating', 'comment']
    
    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("La note doit être comprise entre 1 et 5.")
        return value
    
    def validate(self, attrs):
        user = self.context['request'].user
        destination = attrs['destination']
        
        if DestinationReview.objects.filter(user=user, destination=destination).exists():
            raise serializers.ValidationError("Vous avez déjà laissé un avis sur cette destination.")
        
        return attrs
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)