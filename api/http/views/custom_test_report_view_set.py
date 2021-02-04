from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from api.http.filters import CustomTestReportFilter
from api.http.serializers import CustomTestReportSerializer
from api.http.views.view import BaseViewSet
from api.models import CustomTestReport
from api.permissions import IsSuperuser


class CustomTestReportViewSet(BaseViewSet, ModelViewSet):
    _request_permissions = {
        'update': (IsAuthenticated, IsSuperuser,),
        'partial_update': (IsAuthenticated, IsSuperuser,),
        'create': (IsAuthenticated, IsSuperuser),
        'retrieve': (IsAuthenticated, IsSuperuser),
        'list': (IsAuthenticated, IsSuperuser),
        'destroy': (IsAuthenticated, IsSuperuser),
    }

    serializer_class = CustomTestReportSerializer
    queryset = CustomTestReport.objects.all()
    filterset_class = CustomTestReportFilter
    search_fields = []
