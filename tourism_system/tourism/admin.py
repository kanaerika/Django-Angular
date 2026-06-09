from django.contrib import admin
from django.utils.html import format_html
from .models import Destination, Hotel, HotelBooking, DestinationReview

@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'city', 'created_at', 'image_preview']
    search_fields = ['name', 'city', 'description']
    list_filter = ['created_at']
    readonly_fields = ['created_at', 'image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="80" style="object-fit: cover;" />', obj.image.url)
        return "-"
    image_preview.short_description = "Aperçu"


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'destination', 'address', 'image_preview']
    search_fields = ['name', 'address']
    list_filter = ['destination']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="80" style="object-fit: cover;" />', obj.image.url)
        return "-"
    image_preview.short_description = "Aperçu"


@admin.register(HotelBooking)
class HotelBookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'hotel', 'check_in', 'check_out', 'guests', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'check_in']
    search_fields = ['user__username', 'hotel__name']
    readonly_fields = ['created_at']
    list_editable = ['status']


@admin.register(DestinationReview)
class DestinationReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'destination', 'rating', 'comment_preview', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'destination__name', 'comment']
    readonly_fields = ['created_at']
    
    def comment_preview(self, obj):
        return obj.comment[:50] + "..." if len(obj.comment) > 50 else obj.comment
    comment_preview.short_description = "Commentaire"