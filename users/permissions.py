from rest_framework import permissions


class IsModer(permissions.BasePermission):
    """Проверяем, является ли пользователь модератором"""

    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(
            request.user, "is_moderator", False
        )


class IsOwner(permissions.BasePermission):
    """Проверяем, является ли пользователь владельцем объекта"""

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
