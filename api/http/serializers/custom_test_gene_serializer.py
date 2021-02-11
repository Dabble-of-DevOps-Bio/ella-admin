from rest_framework import serializers
from rest_framework.fields import IntegerField, CharField

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.http.serializers.custom_test_variation_serializer import CustomTestVariationSerializer
from api.http.validators import ExistsValidator
from api.models import CustomTest, CustomTestGene


class CustomTestGeneSerializer(BaseModelSerializer):
    class Meta:
        model = CustomTestGene
        fields = (
            'id', 'name', 'transcript', 'custom_test', 'custom_test_variations',
        )

    id = IntegerField(required=False, validators=[ExistsValidator(queryset=CustomTestGene.objects.all())])

    name = CharField()
    transcript = CharField(required=False)

    custom_test = serializers.PrimaryKeyRelatedField(queryset=CustomTest.objects.all(), required=False)
    custom_test_variations = CustomTestVariationSerializer(source='customtestvariation_set', required=False, many=True)

    def create(self, validated_data):
        custom_test_variations = None
        if 'customtestvariation_set' in validated_data:
            custom_test_variations = validated_data.pop('customtestvariation_set')

        custom_test_gene = CustomTestGene(**validated_data)
        custom_test_gene.save()

        if custom_test_variations is not None:
            self.__create_custom_test_variations(custom_test_variations, custom_test_gene)

        return custom_test_gene

    def update(self, instance: CustomTestGene, validated_data):
        custom_test_variations = []
        if 'customtestvariation_set' in validated_data:
            custom_test_variations = validated_data.pop('customtestvariation_set')

        self.__sync_custom_test_variations(custom_test_variations, instance)

        return super().update(instance, validated_data)

    def bulk_create(self, custom_report_genes: list, custom_test: CustomTest) -> None:
        genes = self.__add_genes_to_test(custom_report_genes, custom_test)

        for gene in genes:
            self.create(gene)

    def bulk_update(self, custom_report_genes: list) -> None:
        for data in custom_report_genes:
            instance = CustomTestGene.objects.get(pk=data['id'])

            self.update(instance, data)

    def __create_custom_test_variations(self, custom_test_variations: list, custom_test_gene: CustomTestGene) -> None:
        custom_test_variation_serializer = CustomTestVariationSerializer()
        custom_test_variation_serializer.bulk_create(custom_test_variations, custom_test_gene)

    def __update_custom_test_variations(self, custom_test_variations: list) -> None:
        if custom_test_variations is not None and len(custom_test_variations) > 0:
            custom_test_variation_serializer = CustomTestVariationSerializer()
            custom_test_variation_serializer.bulk_update(custom_test_variations)

    def __sync_custom_test_variations(self, custom_test_variations: list, custom_test_gene: CustomTestGene) -> None:
        if custom_test_variations is not None:
            self.__remove_not_existed_variantions(custom_test_variations, custom_test_gene)

            new_genes, existed_genes = self._divide_data(custom_test_variations)

            self.__create_custom_test_variations(new_genes, custom_test_gene)
            self.__update_custom_test_variations(existed_genes)

    def __add_genes_to_test(self, custom_report_genes: list, custom_test: CustomTest) -> list:
        for gene in custom_report_genes:
            gene['custom_test'] = custom_test

        return custom_report_genes

    def __remove_not_existed_variantions(self, custom_report_genes, custom_test):
        existing_ids = [entity['id'] for entity in custom_report_genes if 'id' in entity]

        custom_test.customtestvariation_set.exclude(pk__in=existing_ids).delete()
