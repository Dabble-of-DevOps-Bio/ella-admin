from rest_framework import fields
from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import UserGroup


class UserGroupSerializer(BaseModelSerializer):
    class Meta:
        model = UserGroup
        fields = ('id', 'name',)

    id = fields.ReadOnlyField()
    name = fields.CharField(required=True, max_length=255)
