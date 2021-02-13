from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from api.http.filters import CustomTestGeneFilter
from api.http.serializers.custom_test_gene_serializer import CustomTestGeneSerializer
from api.http.views.view import BaseViewSet
from api.models import CustomTestGene
from api.permissions import IsSuperuser


class CustomTestGeneViewSet(BaseViewSet, ModelViewSet):
    _request_permissions = {
        'update': (IsAuthenticated, IsSuperuser,),
        'partial_update': (IsAuthenticated, IsSuperuser,),
        'create': (IsAuthenticated, IsSuperuser),
        'retrieve': (IsAuthenticated, IsSuperuser),
        'list': (IsAuthenticated, IsSuperuser),
        'destroy': (IsAuthenticated, IsSuperuser),
    }

    serializer_class = CustomTestGeneSerializer
    queryset = CustomTestGene.objects.all()
    filterset_class = CustomTestGeneFilter
    search_fields = ['name', 'transcript']
