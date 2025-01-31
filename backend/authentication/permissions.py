from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    """ Custom permission to allow only admins """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'

class IsManager(BasePermission):
    """ Custom permission to allow only managers """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'manager'

class IsUser(BasePermission):
    """ Custom permission to allow only regular users """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'user'
