from rest_framework.permissions import BasePermission
from .models import User

class IsAdminRole(BasePermission):
    message='only admins can do this.'

    def has_permission(self, request, view):
        user=request.user
        return bool(user and user.is_authenticated and user.role== user.Role.ADMIN)
    
class IsVerifiedRescuer(BasePermission):
    message='only verified rescuers can do this.'

    def has_permission(self,request,view):

        user = request.user
        return bool(
            user and user.is_authenticated
            and user.role== user.Role.RESCUER
            and user.is_verified
        )
    
    
class IsVerifiedShelter(BasePermission):
    message='only verified shelters can do this.'

    def has_permission(self,request,view):

        user = request.user
        return bool(
            user and user.is_authenticated
            and user.role== user.Role.SHELTER
            and user.is_verified
        )