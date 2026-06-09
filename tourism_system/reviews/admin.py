from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'activity', 'rating', 'title', 'is_visible', 'created_at']
    list_filter = ['rating', 'is_visible', 'created_at']
    search_fields = ['user__username', 'activity__title', 'title', 'comment']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['make_visible', 'make_hidden']
    
    def make_visible(self, request, queryset):
        queryset.update(is_visible=True)
    make_visible.short_description = "Rendre les avis visibles"
    
    def make_hidden(self, request, queryset):
        queryset.update(is_visible=False)
    make_hidden.short_description = "Masquer les avis"