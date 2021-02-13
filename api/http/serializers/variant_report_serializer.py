import json

from rest_framework import serializers
from rest_framework.fields import CharField

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import VariantReport
from pydash import get


class VariantReportSerializer(BaseModelSerializer):
    class Meta:
        model = VariantReport
        fields = (
            'data', 'comment', 'literature', 'created_at', 'updated_at',
        )

    data = serializers.SerializerMethodField(method_name='get_data')

    comment = CharField(required=False)
    literature = CharField(required=False)

    def get_data(self, obj: VariantReport):
        return json.loads(obj.data)

    def set_report_data_from_validated_data(self):
        if self.instance is not None and get(self, 'validated_data.data') is not None:
            self.instance.data = json.dumps(self.validated_data['data'])
