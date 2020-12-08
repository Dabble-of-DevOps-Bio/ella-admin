from rest_framework import fields
from rest_framework.fields import CharField

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import VariantReport


class VariantReportSerializer(BaseModelSerializer):
    class Meta:
        model = VariantReport
        fields = (
            'data', 'comment', 'literature', 'created_at', 'updated_at',
        )

    data = fields.JSONField()

    comment = CharField(required=False)
    literature = CharField(required=False)
