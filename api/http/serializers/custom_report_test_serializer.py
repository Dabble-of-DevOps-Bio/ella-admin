import pydash

from rest_framework.fields import ReadOnlyField, CharField, ChoiceField

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.http.serializers.custom_report_gene_serializer import CustomReportGeneSerializer
from api.http.serializers.custom_report_result_serializer import CustomReportResultSerializer
from api.http.serializers.custom_report_interpretation_serializer import CustomReportInterpretationSerializer
from api.http.serializers.custom_report_full_report_serializer import CustomReportFullReportSerializer
from api.models import CustomReportTest


class CustomReportTestSerializer(BaseModelSerializer):
    class Meta:
        model = CustomReportTest
        fields = (
            'id', 'name', 'type', 'method', 'disclaimer', 'custom_report_genes',
            'custom_report_result', 'custom_report_interpretation',
            'custom_report_full_report'
        )

    id = ReadOnlyField()
    name = CharField()
    type = ChoiceField(choices=CustomReportTest.Type.choices)
    method = CharField(required=False)
    disclaimer = CharField(required=False)

    custom_report_genes = CustomReportGeneSerializer(source='customreportgene_set', required=False, many=True)

    custom_report_interpretation = CustomReportInterpretationSerializer(source='customreportinterpretation', required=False)
    custom_report_result = CustomReportResultSerializer(source='customreportresult', required=False)

    custom_report_full_report = CustomReportFullReportSerializer(source='customreportfullreport', required=False)

    def create(self, validated_data):
        custom_report_genes = []
        if 'customreportgene_set' in validated_data:
            custom_report_genes = validated_data.pop('customreportgene_set')

        custom_report_full_report = None
        if 'customreportfullreport' in validated_data:
            custom_report_full_report = validated_data.pop('customreportfullreport')

        custom_report_interpretation = None
        if 'customreportinterpretation' in validated_data:
            custom_report_interpretation = validated_data.pop('customreportinterpretation')

        custom_report_result = None
        if 'customreportresult' in validated_data:
            custom_report_result = validated_data.pop('customreportresult')

        custom_report_test = CustomReportTest(**validated_data)

        custom_report_test.save()

        if custom_report_genes is not None:
            self.__create_custom_report_genes(custom_report_genes, custom_report_test)

        if custom_report_result is not None:
            self.__create_custom_report_result(custom_report_result, custom_report_test)

        if custom_report_interpretation is not None:
            self.__create_custom_report_interpretation(custom_report_interpretation, custom_report_test)

        if custom_report_full_report is not None:
            self.__create_custom_report_full_report(custom_report_full_report, custom_report_test)

        return custom_report_test

    def update(self, instance: CustomReportTest, validated_data):
        custom_report_genes = []
        if 'customreportgene_set' in validated_data:
            custom_report_genes = validated_data.pop('customreportgene_set')

        if 'customreportresult' in validated_data:
            custom_report_result = validated_data.pop('customreportresult')

            if 'id' in custom_report_result:
                self.__update_custom_report_result(custom_report_result, instance)
            else:
                self.__create_custom_report_result(custom_report_result, instance)

        if 'customreportinterpretation' in validated_data:
            custom_report_interpretation = validated_data.pop('customreportinterpretation')

            if 'id' in custom_report_interpretation:
                self.__update_custom_report_interpretation(custom_report_interpretation, instance)
            else:
                self.__create_custom_report_interpretation(custom_report_interpretation, instance)

        if 'customreportfullreport' in validated_data:
            custom_report_full_report = validated_data.pop('customreportfullreport')

            if 'id' in custom_report_full_report:
                self.__update_custom_report_full_report(custom_report_full_report, instance)
            else:
                self.__create_custom_report_full_report(custom_report_full_report, instance)

        self.__sync_custom_report_genes(custom_report_genes, instance)

        return super().update(instance, validated_data)

    def __create_custom_report_genes(self, custom_report_genes: list, custom_report_test: CustomReportTest) -> None:
        if custom_report_genes is not None and len(custom_report_genes) > 0:
            custom_report_gene_serializer = CustomReportGeneSerializer()
            custom_report_gene_serializer.bulk_create(custom_report_genes, custom_report_test)

    def __update_custom_report_genes(self, custom_report_genes: list) -> None:
        if custom_report_genes is not None and len(custom_report_genes) > 0:
            custom_report_gene_serializer = CustomReportGeneSerializer()
            custom_report_gene_serializer.bulk_update(custom_report_genes)

    def __create_custom_report_full_report(self, custom_report_full_report, custom_report_test) -> None:
        if pydash.get(custom_report_test, 'customreportfullreport') is not None:
            custom_report_test.customreportfullreport.delete()

        custom_report_full_report_serializer = CustomReportFullReportSerializer()
        custom_report_full_report['custom_report_test'] = custom_report_test

        custom_report_full_report_serializer.create(custom_report_full_report)

    def __update_custom_report_full_report(self, custom_report_full_report, custom_report_test) -> None:
        custom_report_full_report_serializer = CustomReportFullReportSerializer()
        custom_report_full_report_serializer.update(custom_report_test, custom_report_full_report)

    def __create_custom_report_result(self, custom_report_result, custom_report_test) -> None:
        if pydash.get(custom_report_test, 'customreportresult') is not None:
            custom_report_test.customreportresult.delete()

        custom_report_result_serializer = CustomReportResultSerializer()
        custom_report_result['custom_report_test'] = custom_report_test

        custom_report_result_serializer.create(custom_report_result)

    def __update_custom_report_result(self, custom_report_result, custom_report_test) -> None:
        custom_report_result_serializer = CustomReportResultSerializer()
        custom_report_result_serializer.update(custom_report_test, custom_report_result)

    def __create_custom_report_interpretation(self, custom_report_interpretation, custom_report_test) -> None:
        if pydash.get(custom_report_test, 'customreportinterpretation') is not None:
            custom_report_test.customreportinterpretation.delete()

        custom_report_result_serializer = CustomReportInterpretationSerializer()
        custom_report_interpretation['custom_report_test'] = custom_report_test

        custom_report_result_serializer.create(custom_report_interpretation)

    def __update_custom_report_interpretation(self, custom_report_interpretation, custom_report_test) -> None:
        custom_report_interpretation_serializer = CustomReportInterpretationSerializer()
        custom_report_interpretation_serializer.update(custom_report_test, custom_report_interpretation)

    def __sync_custom_report_genes(self, custom_report_genes: list, custom_report_test: CustomReportTest) -> None:
        if custom_report_genes is not None:
            self.__remove_not_existed_genes(custom_report_genes, custom_report_test)

            new_genes, existed_genes = self._divide_data(custom_report_genes)


            self.__create_custom_report_genes(new_genes, custom_report_test)
            self.__update_custom_report_genes(existed_genes)

    def __remove_not_existed_genes(self, custom_report_genes, custom_report_test):
        existing_ids = [entity['id'] for entity in custom_report_genes if 'id' in entity]

        custom_report_test.customreportgene_set.exclude(pk__in=existing_ids).delete()
