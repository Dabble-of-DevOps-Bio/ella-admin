import pydash
from rest_framework import serializers
from rest_framework.fields import ReadOnlyField, CharField

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.http.serializers.custom_test_report_gene_serializer import CustomTestReportGeneSerializer
from api.http.serializers.custom_test_report_interpretation_serializer import CustomTestReportInterpretationSerializer
from api.http.serializers.custom_test_report_result_serializer import CustomTestReportResultSerializer
from api.http.serializers.custom_test_report_variation_serializer import CustomTestReportVariationSerializer
from api.models import CustomTestReport, CustomTest


class CustomTestReportSerializer(BaseModelSerializer):
    class Meta:
        model = CustomTestReport
        fields = (
            'id', 'comments', 'custom_test', 'custom_test_report_genes', 'custom_test_report_variations',
            'custom_test_report_result', 'custom_test_report_interpretation',
        )

    id = ReadOnlyField()

    comments = CharField(required=False)

    custom_test = serializers.PrimaryKeyRelatedField(queryset=CustomTest.objects.all(), required=True)

    custom_test_report_genes = CustomTestReportGeneSerializer(source='customtestreportgene_set', required=False, many=True)
    custom_test_report_variations = CustomTestReportVariationSerializer(source='customtestreportvariation_set', required=False, many=True)

    custom_test_report_interpretation = CustomTestReportInterpretationSerializer(source='customtestreportinterpretation', required=False)
    custom_test_report_result = CustomTestReportResultSerializer(source='customtestreportresult', required=False)

    def create(self, validated_data):
        custom_test_report_genes = []
        if 'customtestreportgene_set' in validated_data:
            custom_test_report_genes = validated_data.pop('customtestreportgene_set')

        custom_test_report_variations = []
        if 'customtestreportvariation_set' in validated_data:
            custom_test_report_variations = validated_data.pop('customtestreportvariation_set')

        custom_test_report_interpretation = None
        if 'customtestreportinterpretation' in validated_data:
            custom_test_report_interpretation = validated_data.pop('customtestreportinterpretation')

        custom_test_report_result = None
        if 'customtestreportresult' in validated_data:
            custom_test_report_result = validated_data.pop('customtestreportresult')

        custom_test_report = CustomTestReport(**validated_data)

        custom_test_report.save()

        if custom_test_report_genes is not None:
            self.__create_custom_test_report_genes(custom_test_report_genes, custom_test_report)

        if custom_test_report_variations is not None:
            self.__create_custom_test_report_variations(custom_test_report_variations, custom_test_report)

        if custom_test_report_result is not None:
            self.__create_custom_test_report_result(custom_test_report_result, custom_test_report)

        if custom_test_report_interpretation is not None:
            self.__create_custom_report_interpretation(custom_test_report_interpretation, custom_test_report)

        return custom_test_report

    def update(self, instance: CustomTestReport, validated_data):
        custom_test_report_genes = []
        if 'customtestreportgene_set' in validated_data:
            custom_test_report_genes = validated_data.pop('customtestreportgene_set')

        custom_test_report_variations = []
        if 'customtestreportvariation_set' in validated_data:
            custom_test_report_variations = validated_data.pop('customtestreportvariation_set')

        if 'customtestreportresult' in validated_data:
            custom_test_report_result = validated_data.pop('customtestreportresult')

            if 'id' in custom_test_report_result:
                self.__update_custom_report_result(custom_test_report_result, instance)
            else:
                self.__create_custom_test_report_result(custom_test_report_result, instance)

        if 'customtestreportinterpretation' in validated_data:
            custom_test_report_interpretation = validated_data.pop('customtestreportinterpretation')

            if 'id' in custom_test_report_interpretation:
                self.__update_custom_report_interpretation(custom_test_report_interpretation, instance)
            else:
                self.__create_custom_report_interpretation(custom_test_report_interpretation, instance)

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

    def __create_custom_test_report_result(self, custom_test_report_result, custom_test_report) -> None:
        if pydash.get(custom_test_report, 'customtestreportresult') is not None:
            custom_test_report.customtestreportresult.delete()

        custom_test_report_result_serializer = CustomTestReportResultSerializer()
        custom_test_report_result['custom_test_report'] = custom_test_report

        custom_test_report_result_serializer.create(custom_test_report_result)

    def __update_custom_report_result(self, custom_test_report_result, custom_test_report) -> None:
        custom_test_report_result_serializer = CustomTestReportResultSerializer()
        custom_test_report_result_serializer.update(custom_test_report, custom_test_report_result)

    def __create_custom_report_interpretation(self, custom_test_report_interpretation, custom_test_report) -> None:
        if pydash.get(custom_test_report, 'customtestreportinterpretation') is not None:
            custom_test_report.customtestreportinterpretation.delete()

        custom_test_report_interpretation_serializer = CustomTestReportInterpretationSerializer()
        custom_test_report_interpretation['custom_test_report'] = custom_test_report

        custom_test_report_interpretation_serializer.create(custom_test_report_interpretation)

    def __update_custom_report_interpretation(self, custom_test_report_interpretation, custom_test) -> None:
        custom_test_report_interpretation_serializer = CustomTestReportInterpretationSerializer()
        custom_test_report_interpretation_serializer.update(custom_test, custom_test_report_interpretation)

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
