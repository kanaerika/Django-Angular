from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Activity, ActivityImage, Schedule

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


class ActivityImageInline(admin.TabularInline):
    model = ActivityImage
    extra = 1
    fields = ['image', 'is_cover', 'order', 'preview']
    readonly_fields = ['preview']
    
    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" style="object-fit: cover;" />', obj.image.url)
        return "-"
    preview.short_description = "Aperçu"


class ScheduleInline(admin.TabularInline):
    model = Schedule
    extra = 1
    fields = ['date', 'start_time', 'available_spots', 'price_override']
    ordering = ['date', 'start_time']


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'city', 'base_price', 'duration_hours', 'is_active', 'cached_rating', 'created_at']
    list_filter = ['is_active', 'city', 'categories', 'created_at']
    search_fields = ['title', 'description', 'slug']
    readonly_fields = ['slug', 'cached_rating', 'created_at', 'updated_at']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['categories']
    inlines = [ActivityImageInline, ScheduleInline]
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('title', 'slug', 'city', 'categories', 'description')
        }),
        ('Détails pratiques', {
            'fields': ('what_to_bring', 'base_price', 'max_travelers', 'duration_hours')
        }),
        ('Statut', {
            'fields': ('is_active', 'cached_rating', 'created_by')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ActivityImage)
class ActivityImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'activity', 'is_cover', 'order', 'image_preview']
    list_filter = ['is_cover', 'activity']
    list_editable = ['is_cover', 'order']
    search_fields = ['activity__title']
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="150" height="100" style="object-fit: cover;" />', obj.image.url)
        return "-"
    image_preview.short_description = "Aperçu"


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['id', 'activity', 'date', 'start_time', 'available_spots', 'price_override', 'is_full']
    list_filter = ['date', 'activity__city', 'activity']
    search_fields = ['activity__title']
    list_editable = ['available_spots', 'price_override']
    date_hierarchy = 'date'
    
    def is_full(self, obj):
        return obj.available_spots == 0
    is_full.boolean = True
    is_full.short_description = "Complet"