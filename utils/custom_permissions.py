from rest_framework.permissions import BasePermission
from users.enums import UserRole


class IsAdminUser(BasePermission):
    """
    Allows access only to users with the ADMIN role.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.role == UserRole.ADMIN.value)
