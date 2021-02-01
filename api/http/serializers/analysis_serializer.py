from rest_framework.fields import CharField, DateTimeField

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import Analysis


class AnalysisSerializer(BaseModelSerializer):
    class Meta:
        model = Analysis
        fields = (
            'id', 'name', 'gene_panel_name', 'gene_panel_version', 'warnings', 'report', 'date_deposited',
            'date_requested',
        )

    name = CharField(read_only=True)

    gene_panel_name = CharField(read_only=True)
    gene_panel_version = CharField(read_only=True)

    warnings = CharField(read_only=True)
    report = CharField(read_only=True)
    date_deposited = DateTimeField(read_only=True)
    date_requested = DateTimeField(read_only=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    def delete(self, instance, validated_data):
        pass
