from rest_framework import permissions

class IsActiveVarified(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return bool(
            request.user.is_active and 
            getattr(request.user, 'is_valified', False) and
            not getattr(request.user, 'is_locked', False)
        )

class IsAdminOrMkurugenzi(permissions.BasePermission):
    def has_permission(self, request, view):
        # FIX YA AnonymousUser has no attribute 'role'
        if not request.user or not request.user.is_authenticated:
            return False
        role = getattr(request.user, 'role', None)
        return role in ['ADMIN', 'MKURUGENZI']

class IsMkurugenziOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        role = getattr(request.user, 'role', None)
        return role == 'MKURUGENZI'