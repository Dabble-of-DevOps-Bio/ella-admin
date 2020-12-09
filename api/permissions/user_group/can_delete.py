from rest_framework.permissions import BasePermission

from api.models import User, GenePanel


class CanDelete(BasePermission):
    def has_permission(self, request, view):
        group_id = view.kwargs['pk']

        return not User.objects.filter(group__pk=view.kwargs['pk']).exists() and not GenePanel.objects.filter(
            groups__pk=group_id).exists()
