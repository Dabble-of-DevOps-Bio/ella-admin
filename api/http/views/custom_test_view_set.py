from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from api.http.filters import CustomTestFilter
from api.http.serializers import CustomTestSerializer
from api.http.views.view import BaseViewSet
from api.models import CustomTest
from api.permissions import IsSuperuser


class CustomTestViewSet(BaseViewSet, ModelViewSet):
    _request_permissions = {
        'update': (IsAuthenticated, IsSuperuser,),
        'partial_update': (IsAuthenticated, IsSuperuser,),
        'create': (IsAuthenticated, IsSuperuser),
        'retrieve': (IsAuthenticated, IsSuperuser),
        'list': (IsAuthenticated, IsSuperuser),
        'destroy': (IsAuthenticated, IsSuperuser),
    }

    serializer_class = CustomTestSerializer
    queryset = CustomTest.objects.all()
    filterset_class = CustomTestFilter
    search_fields = ['name',]
