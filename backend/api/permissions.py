from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrReadOnly(BasePermission):
    """
    Разрешение для проверки, является ли пользователь администратором
    или имеет только права на чтение (SAFE_METHODS).
    """
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS or request.user.is_staff)


class IsAuthorOrReadOnly(BasePermission):
    """
    Разрешение для проверки, является ли пользователь автором
    объекта или имеет только права на чтение (SAFE_METHODS).
    """
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS or obj.author == request.user)
