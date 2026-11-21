from rest_framework.permissions import BasePermission


class HasCompanyPermission(BasePermission):
    message = "User is not associated with a company"

    def has_permission(self, request, view):
        return bool(request.user.company_id)