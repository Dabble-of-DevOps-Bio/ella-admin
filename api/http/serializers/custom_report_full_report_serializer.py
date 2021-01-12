from rest_framework.fields import ReadOnlyField, CharField, IntegerField, DateTimeField

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import CustomReportTest


class CustomReportFullReportSerializer(BaseModelSerializer):
    class Meta:
        model = CustomReportTest
        fields = (
            'id', 'patient_id', 'report_text', 'time_submitted',
        )

    id = ReadOnlyField()
    patient_id = IntegerField(required=False)
    report_text = CharField()
    time_submitted = DateTimeField(read_only=True)

    def create(self, validated_data):
        pass

    def update(self, instance: CustomReportTest, validated_data):
        pass

    def delete(self, instance, validated_data):
        pass
