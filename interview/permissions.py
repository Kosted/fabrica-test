from rest_framework.generics import get_object_or_404
from rest_framework.permissions import BasePermission

from users.models import CustomToken


class IsAuthorized(BasePermission):
    """
    Allows access only to authorized users.
    """

    def has_permission(self, request, view):
        request_token = request.META.get('HTTP_AUTHORIZATION')
        if request_token:
            db_token = get_object_or_404(CustomToken, key=request_token.split(' ')[1])
            return db_token.is_fresh()
        return False
