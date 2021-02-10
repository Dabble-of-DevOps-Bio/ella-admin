from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from api.http.filters import PatientFilter
from api.http.serializers.patient_serializer import PatientSerializer
from api.http.views.view import BaseViewSet
from api.models import Patient
from api.permissions import IsSuperuser


class PatientViewSet(BaseViewSet, ModelViewSet):
    _request_permissions = {
        'update': (IsAuthenticated, IsSuperuser,),
        'partial_update': (IsAuthenticated, IsSuperuser,),
        'create': (IsAuthenticated, IsSuperuser),
        'retrieve': (IsAuthenticated, IsSuperuser),
        'list': (IsAuthenticated, IsSuperuser),
        'destroy': (IsAuthenticated, IsSuperuser),
    }

    serializer_class = PatientSerializer
    queryset = Patient.objects.all()
    filterset_class = PatientFilter
    search_fields = ['name', 'birthday', 'gender', 'sample_type', 'sample_id',
                     'test_accession', 'test_ordered', 'test_code', 'ordered_by',
                     'sample_collection_date', 'sample_accession_date', 'report_date']
