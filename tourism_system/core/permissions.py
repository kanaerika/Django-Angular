from rest_framework import permissions

class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    """
    Permission qui permet la lecture à tous, mais l'écriture seulement aux utilisateurs authentifiés
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission qui permet la lecture à tous, mais la modification seulement au propriétaire
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Vérifier si l'objet a un attribut 'user' ou 'created_by'
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        
        return False


class IsAdminUser(permissions.BasePermission):
    """
    Permission qui permet l'accès seulement aux administrateurs
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_staff