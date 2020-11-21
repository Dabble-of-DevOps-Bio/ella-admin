from rest_framework import fields
from django.utils.translation import gettext as _
from rest_framework.validators import UniqueValidator
from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import User, UserGroup


class UserGroupSerializer(BaseModelSerializer):
    class Meta:
        model = UserGroup
        fields = ('id', 'name',)

    id = fields.ReadOnlyField()
    name = fields.CharField(required=True, max_length=255, validators=[
        UniqueValidator(queryset=UserGroup.objects.all(), message=_('A group with current name already exists.')),
        UniqueValidator(queryset=UserGroup.deleted_objects.all(),
                        message=_('Current group was deleted.'))
    ])
