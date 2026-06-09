from django.contrib import admin
from django.contrib.admin import SimpleListFilter

class DateRangeFilter(SimpleListFilter):
    """
    Filtre personnalisé pour les dates
    """
    title = 'Période'
    parameter_name = 'date_range'
    
    def lookups(self, request, model_admin):
        return (
            ('today', "Aujourd'hui"),
            ('week', 'Cette semaine'),
            ('month', 'Ce mois-ci'),
            ('year', 'Cette année'),
        )
    
    def queryset(self, request, queryset):
        from django.utils import timezone
        from datetime import timedelta
        
        today = timezone.now().date()
        
        if self.value() == 'today':
            return queryset.filter(created_at__date=today)
        elif self.value() == 'week':
            start = today - timedelta(days=today.weekday())
            return queryset.filter(created_at__date__gte=start)
        elif self.value() == 'month':
            return queryset.filter(created_at__year=today.year, created_at__month=today.month)
        elif self.value() == 'year':
            return queryset.filter(created_at__year=today.year)
        
        return queryset