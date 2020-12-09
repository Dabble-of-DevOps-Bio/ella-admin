from django.utils.translation import gettext as _
from rest_framework import fields
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import UserGroup


class UserGroupSerializer(BaseModelSerializer):
    class Meta:
        model = UserGroup
        fields = ('id', 'name',)
        expandable_fields = {
            'users_count': (serializers.SerializerMethodField, {'method_name': 'users_count'}),
            'gene_panels_count': (serializers.SerializerMethodField, {'method_name': 'gene_panels_count'}),
        }

    id = fields.ReadOnlyField()
    name = fields.CharField(required=True, max_length=255, validators=[
        UniqueValidator(queryset=UserGroup.objects.all(), message=_('A group with current name already exists.'))
    ])

    def users_count(self, obj: UserGroup):
        return int(obj.user_set.all().count())

    def gene_panels_count(self, obj: UserGroup):
        return int(obj.genepanel_set.all().count())
