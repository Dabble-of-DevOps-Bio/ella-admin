from rest_framework import fields
from rest_framework.exceptions import ValidationError

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import VariantReport


class VariantReportDataSerializer(BaseModelSerializer):
    class Meta:
        model = VariantReport
        fields = (
            'gene', 'variant', 'zygosity', 'variant_classification'
        )

    gene = fields.CharField(max_length=255, required=True)
    variant = fields.CharField(max_length=255, required=True)
    zygosity = fields.CharField(max_length=255, required=True)
    variant_classification = fields.CharField(max_length=255, required=True)

    def validate(self, data):
        for report_row in self.initial_data:
            unknown_keys = set(report_row.keys()) - set(self.fields.keys())
            if unknown_keys:
                raise ValidationError('Got unknown fields: {}'.format(unknown_keys))

        return data
