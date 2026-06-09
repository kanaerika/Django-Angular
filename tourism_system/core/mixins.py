from rest_framework import status
from rest_framework.response import Response
from django.core.cache import cache

class CacheMixin:
    """
    Mixin pour ajouter le caching aux vues
    """
    cache_timeout = 60 * 15  # 15 minutes par défaut
    
    def dispatch(self, request, *args, **kwargs):
        # Vérifier si le caching est activé
        if hasattr(self, 'cache_timeout') and self.cache_timeout:
            # Créer une clé de cache unique basée sur l'URL et les paramètres
            cache_key = self.get_cache_key(request)
            
            # Essayer de récupérer la réponse du cache
            cached_response = cache.get(cache_key)
            if cached_response:
                return cached_response
            
            # Si pas dans le cache, exécuter la vue
            response = super().dispatch(request, *args, **kwargs)
            
            # Mettre en cache si la réponse est réussie
            if response.status_code == status.HTTP_200_OK:
                cache.set(cache_key, response, self.cache_timeout)
            
            return response
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_cache_key(self, request):
        """Générer une clé de cache unique"""
        from hashlib import md5
        cache_key = f"{request.get_full_path()}_{request.META.get('QUERY_STRING', '')}"
        return md5(cache_key.encode()).hexdigest()


class MultipleFieldLookupMixin:
    """
    Mixin pour appliquer la recherche par plusieurs champs
    """
    def get_object(self):
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)
        filter_kwargs = {}
        
        for field in self.lookup_fields:
            if self.kwargs.get(field):
                filter_kwargs[field] = self.kwargs[field]
        
        obj = queryset.get(**filter_kwargs)
        self.check_object_permissions(self.request, obj)
        return obj


class ActionSerializerMixin:
    """
    Mixin pour utiliser différents serializers selon l'action
    """
    action_serializers = {}
    
    def get_serializer_class(self):
        if self.action in self.action_serializers:
            return self.action_serializers[self.action]
        return super().get_serializer_class()