from rest_framework import fields
from django.contrib.postgres.fields import JSONField
from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import UserGroup


class UserGroupSerializer(BaseModelSerializer):
    class Meta:
        model = UserGroup
        fields = ('id', 'name', 'config')

    id = fields.ReadOnlyField()
    name = fields.CharField(required=True, max_length=255)
    config = JSONField()
