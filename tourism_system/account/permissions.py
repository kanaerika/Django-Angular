from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """L'admin peut tout faire, les autres peuvent seulement lire"""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class IsOwnerOrAdmin(permissions.BasePermission):
    """L'utilisateur peut modifier ses propres données, l'admin peut tout modifier"""
    
    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True
        
        # Pour le modèle User
        if hasattr(obj, 'id') and hasattr(request.user, 'id'):
            return obj.id == request.user.id
        
        # Pour le modèle Profile
        if hasattr(obj, 'user'):
            return obj.user.id == request.user.id
        
        return False