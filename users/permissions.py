from rest_framework import permissions


class IsModer(permissions.BasePermission):
    """Проверяем, является ли пользователь модератором"""

    def has_permission(self, request, view):
        return request.usr.groups.filter(name="modersf").exists()


class IsOwner(permissions.BasePermission):
    """Проверяем, является ли пользователь модератором"""

    def has_object_permission(self, request, view, obj):
        if obj.owner == request.user:
            return True
        return False
