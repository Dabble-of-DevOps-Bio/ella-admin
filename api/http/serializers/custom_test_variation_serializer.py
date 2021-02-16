from rest_framework import serializers
from rest_framework.fields import IntegerField, CharField, ChoiceField

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.http.validators import ExistsValidator
from api.models import CustomTestVariation, CustomTestGene


class CustomTestVariationSerializer(BaseModelSerializer):
    class Meta:
        model = CustomTestVariation
        fields = (
            'id', 'variation', 'classification', 'zygosity', 'custom_test_gene',
        )
        expandable_fields = {
            'custom_test_gene': ('api.http.serializers.CustomTestGeneSerializer',)
        }

    id = IntegerField(required=False, validators=[ExistsValidator(queryset=CustomTestVariation.objects.all())])

    variation = CharField()
    classification = ChoiceField(choices=CustomTestVariation.Classification.choices, required=False)
    zygosity = ChoiceField(choices=CustomTestVariation.Zygosity.choices, required=False)

    custom_test_gene = serializers.PrimaryKeyRelatedField(queryset=CustomTestGene.objects.all(), required=False)

    def bulk_create(self, custom_report_variations: list, custom_test_gene: CustomTestGene) -> None:
        variations = self.__add_variations_to_gene(custom_report_variations, custom_test_gene)

        for variation in variations:
            self.create(variation)

    def bulk_update(self, custom_report_variations: list) -> None:
        for data in custom_report_variations:
            instance = CustomTestVariation.objects.get(pk=data['id'])

            self.update(instance, data)

    def __add_variations_to_gene(self, custom_report_variations: list, custom_test_gene: CustomTestGene) -> list:
        for variation in custom_report_variations:
            variation['custom_test_gene'] = custom_test_gene

        return custom_report_variations
