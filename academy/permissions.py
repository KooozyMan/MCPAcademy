from rest_framework.permissions import BasePermission, SAFE_METHODS

from .models import User


class IsStaffOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.method in SAFE_METHODS or request.user.role in {User.Role.ADMIN, User.Role.TEACHER})
        )


class IsAcademyStaff(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in {User.Role.ADMIN, User.Role.TEACHER}
        )
