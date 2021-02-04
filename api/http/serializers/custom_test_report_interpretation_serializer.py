from rest_framework import serializers
from rest_framework.fields import IntegerField, CharField

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.http.validators import ExistsValidator
from api.models import CustomTestReport, CustomTestReportInterpretation


class CustomTestReportInterpretationSerializer(BaseModelSerializer):
    class Meta:
        model = CustomTestReportInterpretation
        fields = (
            'id', 'interpretation', 'custom_test_report'
        )

    id = IntegerField(required=False, validators=[ExistsValidator(queryset=CustomTestReportInterpretation.objects.all())])

    interpretation = CharField()

    custom_test_report = serializers.PrimaryKeyRelatedField(queryset=CustomTestReport.objects.all(), required=False)
