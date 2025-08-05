from rest_framework import permissions


class IsReviewAurthorOrReadOnly(permissions.BasePermission): #View lavel permission, view k k korte parbe
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj): #object level permisssion, object k k access korte parbe edit korte parbe
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_staff:
            return True
        return obj.user == request.user