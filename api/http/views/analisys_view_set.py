from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated

from api.http.filters import AnalysisFilter
from api.http.serializers import AnalysisSerializer
from api.http.views.view import BaseViewSet
from api.models import Analysis
from api.permissions import IsSuperuser


class AnalysisViewSet(BaseViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    _request_permissions = {
        'retrieve': (IsAuthenticated, IsSuperuser),
        'list': (IsAuthenticated, IsSuperuser),
    }

    serializer_class = AnalysisSerializer
    queryset = Analysis.objects.all()
    filterset_class = AnalysisFilter
    search_fields = ['name', 'gene_panel_name', 'gene_panel_version',]
