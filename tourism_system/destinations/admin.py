from django.contrib import admin
from .models import Country, City

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'iso_code', 'created_at']
    search_fields = ['name', 'iso_code']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'country', 'slug', 'created_at']
    list_filter = ['country', 'created_at']
    search_fields = ['name', 'description', 'slug']
    readonly_fields = ['slug', 'created_at', 'updated_at']
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('name', 'slug', 'country', 'description')
        }),
        ('Médias', {
            'fields': ('thumbnail',)
        }),
        ('Coordonnées', {
            'fields': ('latitude', 'longitude'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )