from rest_framework import permissions

class IsUserOrReadOnly(permissions.BasePermission):
    # Allow GET request for every user and POST, PUT, PATCH and DELETE requests for owners
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return obj == request.user

class IsOrganizerOrReadOnly(permissions.BasePermission):  
    # Allow POST request for authenticated users and only GET request for unauthenticated users
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:  
            return True
        return request.user and request.user.is_authenticated
    
    # Allow update and delete of Events objects by organizer
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.organizer == request.user
    
class IsOwnerOrReadOnly(permissions.BasePermission):
    # Allow POST request for authenticated users and only GET request for unauthenticated users
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:  
            return True
        return request.user and request.user.is_authenticated
    
    # Allow update and delete of RSVP objects by user
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user