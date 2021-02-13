from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from api.http.filters import CustomTestVariationFilter
from api.http.serializers.custom_test_report_variation_serializer import CustomTestVariationSerializer
from api.http.views.view import BaseViewSet
from api.models import CustomTestVariation
from api.permissions import IsSuperuser


class CustomTestVariationViewSet(BaseViewSet, ModelViewSet):
    _request_permissions = {
        'update': (IsAuthenticated, IsSuperuser,),
        'partial_update': (IsAuthenticated, IsSuperuser,),
        'create': (IsAuthenticated, IsSuperuser),
        'retrieve': (IsAuthenticated, IsSuperuser),
        'list': (IsAuthenticated, IsSuperuser),
        'destroy': (IsAuthenticated, IsSuperuser),
    }

    serializer_class = CustomTestVariationSerializer
    queryset = CustomTestVariation.objects.all()
    filterset_class = CustomTestVariationFilter
    search_fields = ['variation', 'classification', 'zygosity']
