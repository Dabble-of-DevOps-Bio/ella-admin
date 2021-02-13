from rest_framework import mixins
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.http.filters import AnalysisFilter
from api.http.serializers import AnalysisSerializer
from api.http.views.view import BaseViewSet
from api.models import Analysis
from api.permissions import IsSuperuser
from api.utilities.tests_helpers import load_json


class AnalysisViewSet(BaseViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    _request_permissions = {
        'retrieve': (IsAuthenticated, IsSuperuser),
        'list': (IsAuthenticated, IsSuperuser),
        'get_patient_data': (IsAuthenticated, IsSuperuser),
    }

    serializer_class = AnalysisSerializer
    queryset = Analysis.objects.all()
    filterset_class = AnalysisFilter
    search_fields = ['name', 'gene_panel_name', 'gene_panel_version', ]

    def get_queryset(self):
        return super().get_queryset().filter(gene_panel__groups__pk=self.request.user.group_id)

    @action(methods=['GET'], detail=True)
    def get_patient_data(self, request, *args, **kwargs):
        patient_data = load_json('api/mocks/fixtures/ella_app_api_service/analysis_patient_data.json')

        return Response(data=patient_data, status=status.HTTP_200_OK)
