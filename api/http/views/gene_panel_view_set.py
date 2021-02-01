from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from api.http.filters import GenePanelFilter
from api.http.serializers import GenePanelSerializer
from api.http.views.view import BaseViewSet
from api.models import GenePanel
from api.permissions import IsSuperuser


class GenePanelViewSet(BaseViewSet, ModelViewSet):
    _request_permissions = {
        'update': (IsAuthenticated, IsSuperuser),
        'list': (IsAuthenticated, IsSuperuser),
        'retrieve': (IsAuthenticated, IsSuperuser,),
    }

    serializer_class = GenePanelSerializer
    queryset = GenePanel.objects.all()
    filterset_class = GenePanelFilter
    search_fields = ['name', 'version', ]
