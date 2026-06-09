from django.contrib import admin
from .models import Booking, Payment

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'booking_reference', 'user', 'schedule', 'number_of_travelers',
        'total_price', 'status', 'created_at'
    ]
    list_filter = ['status', 'created_at', 'schedule__date']
    search_fields = ['booking_reference', 'user__username', 'user__email']
    readonly_fields = ['booking_reference', 'created_at', 'updated_at', 'total_price']
    raw_id_fields = ['user', 'schedule']
    
    actions = ['confirm_bookings', 'complete_bookings', 'cancel_bookings']
    
    def confirm_bookings(self, request, queryset):
        queryset.update(status='confirmed')
    confirm_bookings.short_description = "Confirmer les réservations sélectionnées"
    
    def complete_bookings(self, request, queryset):
        queryset.update(status='completed')
    complete_bookings.short_description = "Marquer comme terminées"
    
    def cancel_bookings(self, request, queryset):
        for booking in queryset:
            if booking.status not in ['cancelled', 'refunded', 'completed']:
                booking.status = 'cancelled'
                booking.save()
    cancel_bookings.short_description = "Annuler les réservations sélectionnées"


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'booking', 'method', 'amount_paid', 'is_successful', 'created_at']
    list_filter = ['method', 'is_successful', 'created_at']
    search_fields = ['booking__booking_reference', 'stripe_payment_intent_id']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['booking']