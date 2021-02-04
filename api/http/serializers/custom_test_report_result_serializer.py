from rest_framework import serializers
from rest_framework.fields import IntegerField, CharField, ChoiceField

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.http.validators import ExistsValidator
from api.models import CustomTestReport, CustomTestReportResult


class CustomTestReportResultSerializer(BaseModelSerializer):
    class Meta:
        model = CustomTestReportResult
        fields = (
            'id', 'result', 'finding', 'custom_test_report',
        )

    id = IntegerField(required=False, validators=[ExistsValidator(queryset=CustomTestReportResult.objects.all())])

    result = CharField()
    finding = ChoiceField(choices=CustomTestReportResult.Finding.choices, required=False)

    custom_test_report = serializers.PrimaryKeyRelatedField(queryset=CustomTestReport.objects.all(), required=False)
