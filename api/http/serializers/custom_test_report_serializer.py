from rest_framework import serializers
from rest_framework.fields import ReadOnlyField, CharField

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.http.serializers.custom_test_serializer import CustomTestSerializer
from api.http.serializers.custom_test_report_gene_serializer import CustomTestReportGeneSerializer
from api.http.serializers.custom_test_report_variation_serializer import CustomTestReportVariationSerializer
from api.models import CustomTestReport, CustomTest


class CustomTestReportSerializer(BaseModelSerializer):
    class Meta:
        model = CustomTestReport
        fields = (
            'id', 'interpretation', 'result', 'comments', 'custom_test', 'custom_test_report_genes', 'custom_test_report_variations',
        )
        expandable_fields = {
            'custom_test': (CustomTestSerializer, {'source': 'custom_test'}),
            'custom_test_report_genes': (CustomTestReportGeneSerializer, {'source': 'customtestreportgene_set', 'many': True}),
            'custom_test_report_variations': (CustomTestReportVariationSerializer, {'source': 'customtestreportvariation_set', 'many': True})
        }

    id = ReadOnlyField()

    interpretation = CharField(required=False, allow_blank=True)
    result = CharField(required=False, allow_blank=True)
    comments = CharField(required=False, allow_blank=True)

    custom_test = serializers.PrimaryKeyRelatedField(queryset=CustomTest.objects.all(), required=True)

    custom_test_report_genes = CustomTestReportGeneSerializer(source='customtestreportgene_set', required=False, many=True)
    custom_test_report_variations = CustomTestReportVariationSerializer(source='customtestreportvariation_set', required=False, many=True)

    def create(self, validated_data):
        custom_test_report_genes = []
        if 'customtestreportgene_set' in validated_data:
            custom_test_report_genes = validated_data.pop('customtestreportgene_set')

        custom_test_report_variations = []
        if 'customtestreportvariation_set' in validated_data:
            custom_test_report_variations = validated_data.pop('customtestreportvariation_set')

        custom_test_report = CustomTestReport(**validated_data)

        custom_test_report.save()

        if custom_test_report_genes is not None:
            self.__create_custom_test_report_genes(custom_test_report_genes, custom_test_report)

        if custom_test_report_variations is not None:
            self.__create_custom_test_report_variations(custom_test_report_variations, custom_test_report)

        return custom_test_report

    def update(self, instance: CustomTestReport, validated_data):
        custom_test_report_genes = []
        if 'customtestreportgene_set' in validated_data:
            custom_test_report_genes = validated_data.pop('customtestreportgene_set')

        custom_test_report_variations = []
        if 'customtestreportvariation_set' in validated_data:
            custom_test_report_variations = validated_data.pop('customtestreportvariation_set')

        self.__sync_custom_test_report_genes(custom_test_report_genes, instance)
        self.__sync_custom_test_report_variations(custom_test_report_variations, instance)

        return super().update(instance, validated_data)

    def __create_custom_test_report_genes(self, custom_test_report_genes: list, custom_test_report: CustomTestReport) -> None:
        if custom_test_report_genes is not None and len(custom_test_report_genes) > 0:
            custom_test_report_gene_serializer = CustomTestReportGeneSerializer()
            custom_test_report_gene_serializer.bulk_create(custom_test_report_genes, custom_test_report)

    def __update_custom_test_report_genes(self, custom_test_report_genes: list) -> None:
        if custom_test_report_genes is not None and len(custom_test_report_genes) > 0:
            custom_test_report_gene_serializer = CustomTestReportGeneSerializer()
            custom_test_report_gene_serializer.bulk_update(custom_test_report_genes)

    def __create_custom_test_report_variations(self, custom_test_report_variations: list, custom_test: CustomTestReport) -> None:
        if custom_test_report_variations is not None and len(custom_test_report_variations) > 0:
            custom_test_report_gene_serializer = CustomTestReportVariationSerializer()
            custom_test_report_gene_serializer.bulk_create(custom_test_report_variations, custom_test)

    def __update_custom_test_report_variations(self, custom_test_report_variations: list) -> None:
        if custom_test_report_variations is not None and len(custom_test_report_variations) > 0:
            custom_test_report_variation_serializer = CustomTestReportVariationSerializer()
            custom_test_report_variation_serializer.bulk_update(custom_test_report_variations)

    def __sync_custom_test_report_genes(self, custom_test_report_genes: list, custom_test_report: CustomTestReport) -> None:
        if custom_test_report_genes is not None:
            self.__remove_not_existed_genes(custom_test_report_genes, custom_test_report)

            new_genes, existed_genes = self._divide_data(custom_test_report_genes)

            self.__create_custom_test_report_genes(new_genes, custom_test_report)
            self.__update_custom_test_report_genes(existed_genes)

    def __sync_custom_test_report_variations(self, custom_test_report_variations: list, custom_test_report: CustomTestReport) -> None:
        if custom_test_report_variations is not None:
            self.__remove_not_existed_genes(custom_test_report_variations, custom_test_report)

            new_genes, existed_genes = self._divide_data(custom_test_report_variations)

            self.__create_custom_test_report_variations(new_genes, custom_test_report)
            self.__update_custom_test_report_variations(existed_genes)

    def __remove_not_existed_genes(self, custom_test_report_genes: list, custom_test_report: CustomTestReport):
        existing_ids = [entity['id'] for entity in custom_test_report_genes if 'id' in entity]

        custom_test_report.customtestreportgene_set.exclude(pk__in=existing_ids).delete()
