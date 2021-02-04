from rest_framework import serializers
from rest_framework.fields import IntegerField, CharField

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.http.validators import ExistsValidator
from api.models import CustomTestReportGene, CustomTestReport, CustomTestGene


class CustomTestReportGeneSerializer(BaseModelSerializer):
    class Meta:
        model = CustomTestReportGene
        fields = (
            'id', 'summary', 'custom_test_gene', 'custom_test_report',
        )

    id = IntegerField(required=False, validators=[ExistsValidator(queryset=CustomTestReportGene.objects.all())])

    summary = CharField()

    custom_test_gene = serializers.PrimaryKeyRelatedField(queryset=CustomTestGene.objects.all(), required=False)
    custom_test_report = serializers.PrimaryKeyRelatedField(queryset=CustomTestReport.objects.all(), required=False)

    def bulk_create(self, custom_test_report_genes: list, custom_test_report: CustomTestReport) -> None:
        genes = self.__add_genes_to_report(custom_test_report_genes, custom_test_report)

        for gene in genes:
            self.create(gene)

    def bulk_update(self, custom_report_genes: list) -> None:
        for data in custom_report_genes:
            instance = CustomTestReportGene.objects.get(pk=data['id'])

            self.update(instance, data)

    def __add_genes_to_report(self, custom_test_report_genes: list, custom_test_report: CustomTestReport) -> list:
        for gene in custom_test_report_genes:
            gene['custom_test_report'] = custom_test_report

        return custom_test_report_genes
