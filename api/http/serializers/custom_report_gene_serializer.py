from rest_framework.fields import IntegerField, CharField

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.http.serializers.custom_report_variation_serializer import CustomReportVariationSerializer
from api.models import CustomReportTest, CustomReportGene
from api.http.validators import ExistsValidator


class CustomReportGeneSerializer(BaseModelSerializer):
    class Meta:
        model = CustomReportGene
        fields = (
            'id', 'name', 'summary', 'transcript', 'custom_report_variations'
        )

    id = IntegerField(required=False, validators=[ExistsValidator(queryset=CustomReportGene.objects.all())])
    name = CharField()
    summary = CharField(required=False)
    transcript = CharField(required=False)
    custom_report_variations = CustomReportVariationSerializer(source='customreportvariation_set', required=False, many=True)

    def create(self, validated_data):
        custom_report_variations = None
        if 'customreportvariation_set' in validated_data:
            custom_report_variations = validated_data.pop('customreportvariation_set')

        custom_report_gene = CustomReportGene(**validated_data)
        custom_report_gene.save()

        if custom_report_variations is not None:
            self.__create_custom_report_variations(custom_report_variations, custom_report_gene)

        return custom_report_gene

    def update(self, instance: CustomReportTest, validated_data):
        custom_report_variations = []
        if 'customreportvariation_set' in validated_data:
            custom_report_variations = validated_data.pop('customreportvariation_set')

        self.__sync_custom_report_genes(custom_report_variations, instance)

        return super().update(instance, validated_data)

    def bulk_create(self, custom_report_genes: list, custom_report_test: CustomReportTest) -> None:
        genes = self.__add_genes_to_test(custom_report_genes, custom_report_test)

        for gene in genes:
            self.create(gene)

    def bulk_update(self, custom_report_genes: list) -> None:
        for data in custom_report_genes:
            instance = CustomReportGene.objects.get(pk=data['id'])

            self.update(instance, data)

    def __create_custom_report_variations(self, custom_report_variations: list, custom_report_gene: CustomReportGene) -> None:
        custom_report_variation_serializer = CustomReportVariationSerializer()
        custom_report_variation_serializer.bulk_create(custom_report_variations, custom_report_gene)

    def __update_custom_report_variations(self, custom_report_variations: list) -> None:
        if custom_report_variations is not None and len(custom_report_variations) > 0:
            custom_report_gene_serializer = CustomReportVariationSerializer()
            custom_report_gene_serializer.bulk_update(custom_report_variations)

    def __sync_custom_report_genes(self, custom_report_variations: list, custom_report_gene) -> None:
        if custom_report_variations is not None:
            self.__remove_not_existed_variantions(custom_report_variations, custom_report_gene)

            new_genes, existed_genes = self._divide_data(custom_report_variations)

            self.__create_custom_report_variations(new_genes, custom_report_gene)
            self.__update_custom_report_variations(existed_genes)

    def __add_genes_to_test(self, custom_report_genes: list, custom_report_test: CustomReportTest) -> list:
        for gene in custom_report_genes:
            gene['custom_report_test'] = custom_report_test

        return custom_report_genes

    def __remove_not_existed_variantions(self, custom_report_genes, custom_report_test):
        existing_ids = [entity['id'] for entity in custom_report_genes if 'id' in entity]

        custom_report_test.customreportvariation_set.exclude(pk__in=existing_ids).delete()
