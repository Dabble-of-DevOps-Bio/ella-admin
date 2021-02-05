from rest_framework.fields import ReadOnlyField, CharField, ChoiceField

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.http.serializers.custom_test_gene_serializer import CustomTestGeneSerializer
from api.models import CustomTest


class CustomTestSerializer(BaseModelSerializer):
    class Meta:
        model = CustomTest
        fields = (
            'id', 'name', 'type', 'finding', 'methodology', 'limitations', 'references', 'custom_test_genes',
        )

    id = ReadOnlyField()

    name = CharField()

    type = ChoiceField(choices=CustomTest.Type.choices)
    finding = ChoiceField(choices=CustomTest.Finding.choices)

    methodology = CharField(required=False)
    limitations = CharField(required=False)
    references = CharField(required=False)

    custom_test_genes = CustomTestGeneSerializer(source='customtestgene_set', required=False, many=True)

    def create(self, validated_data):
        custom_test_genes = []
        if 'customtestgene_set' in validated_data:
            custom_test_genes = validated_data.pop('customtestgene_set')

        custom_test = CustomTest(**validated_data)

        custom_test.save()

        if custom_test_genes is not None:
            self.__create_custom_test_genes(custom_test_genes, custom_test)

        return custom_test

    def update(self, instance: CustomTest, validated_data):
        custom_test_genes = []
        if 'customtestgene_set' in validated_data:
            custom_test_genes = validated_data.pop('customtestgene_set')

        self.__sync_custom_test_genes(custom_test_genes, instance)

        return super().update(instance, validated_data)

    def __create_custom_test_genes(self, custom_test_genes: list, custom_test: CustomTest) -> None:
        if custom_test_genes is not None and len(custom_test_genes) > 0:
            custom_report_gene_serializer = CustomTestGeneSerializer()
            custom_report_gene_serializer.bulk_create(custom_test_genes, custom_test)

    def __update_custom_test_genes(self, custom_test_genes: list) -> None:
        if custom_test_genes is not None and len(custom_test_genes) > 0:
            custom_report_gene_serializer = CustomTestGeneSerializer()
            custom_report_gene_serializer.bulk_update(custom_test_genes)

    def __sync_custom_test_genes(self, custom_test_genes: list, custom_test: CustomTest) -> None:
        if custom_test_genes is not None:
            self.__remove_not_existed_genes(custom_test_genes, custom_test)

            new_genes, existed_genes = self._divide_data(custom_test_genes)

            self.__create_custom_test_genes(new_genes, custom_test)
            self.__update_custom_test_genes(existed_genes)

    def __remove_not_existed_genes(self, custom_test_genes: list, custom_test: CustomTest):
        existing_ids = [entity['id'] for entity in custom_test_genes if 'id' in entity]

        custom_test.customtestgene_set.exclude(pk__in=existing_ids).delete()
