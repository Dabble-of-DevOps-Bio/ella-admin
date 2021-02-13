from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from api.http.filters import UserGroupFilter
from api.http.serializers import UserGroupSerializer
from api.http.views.view import BaseViewSet
from api.models import UserGroup
from api.permissions import IsSuperuser, CanDelete


class UserGroupViewSet(BaseViewSet, ModelViewSet):
    _request_permissions = {
        'update': (IsAuthenticated, IsSuperuser,),
        'partial_update': (IsAuthenticated, IsSuperuser,),
        'create': (IsAuthenticated, IsSuperuser),
        'retrieve': (IsAuthenticated, IsSuperuser),
        'list': (IsAuthenticated, IsSuperuser),
        'destroy': (IsAuthenticated, IsSuperuser, CanDelete),
    }

    serializer_class = UserGroupSerializer
    queryset = UserGroup.objects.all()
    filterset_class = UserGroupFilter
    search_fields = ['name']
