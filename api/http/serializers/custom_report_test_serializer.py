from rest_framework.fields import ReadOnlyField, CharField

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.http.serializers.custom_report_gene_serializer import CustomReportGeneSerializer
from api.models import CustomReportTest


class CustomReportTestSerializer(BaseModelSerializer):
    class Meta:
        model = CustomReportTest
        fields = (
            'id', 'name', 'type', 'method', 'disclaimer', 'custom_report_genes'
        )

    id = ReadOnlyField()
    name = CharField()
    type = CharField()
    method = CharField(required=False)
    disclaimer = CharField(required=False)

    custom_report_genes = CustomReportGeneSerializer(source='customreportgene_set', required=False, many=True)

    def create(self, validated_data):
        custom_report_genes = []
        if 'customreportgene_set' in validated_data:
            custom_report_genes = validated_data.pop('customreportgene_set')

        custom_report_test = CustomReportTest(**validated_data)

        custom_report_test.save()

        if custom_report_genes is not None:
            self.__create_custom_report_genes(custom_report_genes, custom_report_test)

        return custom_report_test

    def update(self, instance: CustomReportTest, validated_data):
        custom_report_genes = []
        if 'customreportgene_set' in validated_data:
            custom_report_genes = validated_data.pop('customreportgene_set')

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

    def __sync_custom_report_genes(self, custom_report_genes: list, custom_report_test: CustomReportTest) -> None:
        if custom_report_genes is not None:
            self.__remove_not_existed_genes(custom_report_genes, custom_report_test)

            new_genes, existed_genes = self._divide_data(custom_report_genes)

            self.__create_custom_report_genes(new_genes, custom_report_test)
            self.__update_custom_report_genes(existed_genes)

    def __remove_not_existed_genes(self, custom_report_genes, custom_report_test):
        existing_ids = [entity['id'] for entity in custom_report_genes if 'id' in entity]

        custom_report_test.customreportgene_set.exclude(pk__in=existing_ids).delete()
