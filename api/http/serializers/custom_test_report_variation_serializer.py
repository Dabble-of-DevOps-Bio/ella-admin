from rest_framework import serializers
from rest_framework.fields import IntegerField, CharField

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.http.validators import ExistsValidator
from api.models import CustomTestReport, CustomTestVariation, CustomTestReportVariation


class CustomTestReportVariationSerializer(BaseModelSerializer):
    class Meta:
        model = CustomTestReportVariation
        fields = (
            'id', 'description', 'custom_test_variation', 'custom_test_report',
        )

    id = IntegerField(required=False, validators=[ExistsValidator(queryset=CustomTestReportVariation.objects.all())])

    description = CharField()

    custom_test_variation = serializers.PrimaryKeyRelatedField(queryset=CustomTestVariation.objects.all(), required=False)
    custom_test_report = serializers.PrimaryKeyRelatedField(queryset=CustomTestReport.objects.all(), required=False)

    def bulk_create(self, custom_test_report_variations: list, custom_test_report: CustomTestReport) -> None:
        variations = self.__add_genes_to_report(custom_test_report_variations, custom_test_report)

        for variation in variations:
            self.create(variation)

    def bulk_update(self, custom_test_report_variations: list) -> None:
        for data in custom_test_report_variations:
            instance = CustomTestReportVariation.objects.get(pk=data['id'])

            self.update(instance, data)

    def __add_genes_to_report(self, custom_test_report_variations: list, custom_test_report: CustomTestReport) -> list:
        for variation in custom_test_report_variations:
            variation['custom_test_report'] = custom_test_report

        return custom_test_report_variations
