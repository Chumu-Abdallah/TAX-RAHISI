# core/permission
from rest_framework.permissions import BasePermission


class IsOunerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.created_by == request.user

class IsTaxOfficer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['TAX_OFFICER', 'ADMIN'] 

class IsBusnessOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'business_profile')    