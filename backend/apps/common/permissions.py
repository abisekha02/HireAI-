from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsRecruiterOrAdmin(BasePermission):
    """Allows write access only to recruiters/admins; read access to any authenticated user."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_recruiter


class IsCandidate(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_candidate)


class IsOwnerOrRecruiter(BasePermission):
    """Object-level permission: candidate owns the object, or a recruiter/admin may access it."""

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_recruiter:
            return True
        owner = getattr(obj, "candidate", None) or getattr(obj, "user", None)
        return owner == user


class RoleRequired(BasePermission):
    """Generic factory-style permission: set `required_roles` on the view."""

    def has_permission(self, request, view):
        required_roles = getattr(view, "required_roles", None)
        if not required_roles:
            return True
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in required_roles
        )
