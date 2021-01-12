import pendulum

from rest_framework.fields import ReadOnlyField, CharField, IntegerField, DateTimeField

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import CustomReportFullReport


class CustomReportFullReportSerializer(BaseModelSerializer):
    class Meta:
        model = CustomReportFullReport
        fields = (
            'id', 'patient_id', 'report_text', 'time_submitted',
        )

    id = ReadOnlyField()
    patient_id = IntegerField(required=False)
    report_text = CharField()
    time_submitted = DateTimeField(read_only=True)

    def create(self, validated_data):
        validated_data = self.__set_time_submitted(validated_data)

        custom_report_test = CustomReportFullReport(**validated_data)
        custom_report_test.save()

        return custom_report_test

    def update(self, instance: CustomReportFullReport, validated_data):
        validated_data = self.__set_time_submitted(validated_data)

        return super().update(instance, validated_data)

    def __set_time_submitted(self, validated_data):
        validated_data['time_submitted'] = pendulum.now()

        return validated_data
