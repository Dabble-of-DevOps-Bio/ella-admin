from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from api.http.filters import CustomReportTestFilter
from api.http.serializers import CustomReportTestSerializer
from api.http.views.view import BaseViewSet
from api.models import CustomReportTest
from api.permissions import IsSuperuser


class CustomReportTestViewSet(BaseViewSet, ModelViewSet):
    _request_permissions = {
        'update': (IsAuthenticated, IsSuperuser,),
        'partial_update': (IsAuthenticated, IsSuperuser,),
        'create': (IsAuthenticated, IsSuperuser),
        'retrieve': (IsAuthenticated, IsSuperuser),
        'list': (IsAuthenticated, IsSuperuser),
        'destroy': (IsAuthenticated, IsSuperuser),
    }

    serializer_class = CustomReportTestSerializer
    queryset = CustomReportTest.objects.all()
    filterset_class = CustomReportTestFilter
    search_fields = ['name',]
