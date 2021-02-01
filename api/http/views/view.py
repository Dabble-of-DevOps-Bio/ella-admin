from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import SearchFilter

from api.http.pagination import PageNumberPagination


class BaseViewSet(viewsets.GenericViewSet):
    _request_permissions = []
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend, SearchFilter,)

    def get_serializer(self, *args, **kwargs):
        is_update = self.request.method == 'PUT'
        request_context = {'request': self.request}

        kwargs['partial'] = is_update
        kwargs['context'] = {**kwargs['context'], **request_context} if 'context' in kwargs else request_context

        return self.get_serializer_class()(*args, **kwargs)

    def get_permissions(self):
        try:
            self.permission_classes = self._request_permissions[self.action]

            return super().get_permissions()
        except:
            raise PermissionDenied()
