from rest_framework import mixins
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.http.filters.user_filter import UserFilter
from api.http.serializers import UserSerializer
from api.http.views.view import BaseViewSet
from api.models import User, UserGroup
from api.permissions import IsSuperuser


class UserViewSet(BaseViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.RetrieveModelMixin,
                  mixins.ListModelMixin):
    _request_permissions = {
        'update': (IsAuthenticated, IsSuperuser,),
        'partial_update': (IsAuthenticated, IsSuperuser,),
        'create': (IsAuthenticated, IsSuperuser),
        'retrieve': (IsAuthenticated, IsSuperuser),
        'list': (IsAuthenticated, IsSuperuser),
        'move_to_inactive_group': (IsAuthenticated, IsSuperuser),
    }

    serializer_class = UserSerializer
    queryset = User.objects.all()
    filterset_class = UserFilter
    search_fields = ['first_name', 'last_name', 'email', 'username']

    def get_serializer(self, *args, **kwargs):
        action = {'action': self.action}
        kwargs['context'] = {**kwargs['context'], **action} if 'context' in kwargs else action

        return super().get_serializer(*args, **kwargs)

    @action(methods=['POST'], detail=False)
    def move_to_inactive_group(self, request, *args, **kwargs):
        user_id = kwargs.get('user_pk', None)

        user_group = UserGroup.objects.get(name='inactive')
        User.objects.filter(pk=user_id).update(group_id=user_group.pk)

        return Response(status=status.HTTP_204_NO_CONTENT)
