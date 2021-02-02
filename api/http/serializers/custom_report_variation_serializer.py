import pydash
from rest_framework.fields import IntegerField, CharField, ChoiceField

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.http.serializers.custom_report_result_serializer import CustomReportResultSerializer
from api.http.validators import ExistsValidator
from api.models import CustomReportVariation, CustomReportGene, CustomReportResult


class CustomReportVariationSerializer(BaseModelSerializer):
    class Meta:
        model = CustomReportVariation
        fields = (
            'id', 'variation', 'description', 'classification', 'zygosity', 'custom_report_result'
        )

    id = IntegerField(required=False, validators=[ExistsValidator(queryset=CustomReportVariation.objects.all())])
    variation = CharField()
    description = CharField()
    classification = ChoiceField(choices=CustomReportVariation.Classification.choices)
    zygosity = ChoiceField(choices=CustomReportVariation.Zygosity.choices)
    custom_report_result = CustomReportResultSerializer(source='customreportresult', required=False)

    def create(self, validated_data):
        custom_report_result = None
        if 'customreportresult' in validated_data:
            custom_report_result = validated_data.pop('customreportresult')

        custom_report_variation = CustomReportVariation(**validated_data)

        custom_report_variation.save()

        if custom_report_result is not None:
            self.__create_custom_report_result(custom_report_result, custom_report_variation)

        return custom_report_variation

    def update(self, instance: CustomReportVariation, validated_data):
        if 'customreportresult' in validated_data:
            custom_report_result = validated_data.pop('customreportresult')

            if 'id' in custom_report_result:
                self.__update_custom_report_result(custom_report_result, instance)
            else:
                self.__create_custom_report_result(custom_report_result, instance)

        return super().update(instance, validated_data)

    def bulk_create(self, custom_report_variations: list, custom_report_gene: CustomReportGene) -> None:
        variations = self.__add_variations_to_gene(custom_report_variations, custom_report_gene)

        for variation in variations:
            self.create(variation)

    def bulk_update(self, custom_report_variations: list) -> None:
        for data in custom_report_variations:
            instance = CustomReportVariation.objects.get(pk=data['id'])

            self.update(instance, data)

    def __create_custom_report_result(self, custom_report_result: CustomReportResult,
                                      custom_report_variation: CustomReportVariation) -> None:
        if pydash.get(custom_report_variation, 'customreportresult') is not None:
            custom_report_variation.customreportresult.delete()

        custom_report_result_serializer = CustomReportResultSerializer()
        custom_report_result['custom_report_variation'] = custom_report_variation

        custom_report_result_serializer.create(custom_report_result)

    def __update_custom_report_result(self, custom_report_result: CustomReportResult,
                                      custom_report_variation: CustomReportVariation) -> None:
        custom_report_result_serializer = CustomReportResultSerializer()
        custom_report_result_serializer.update(custom_report_variation.customreportresult, custom_report_result)

    def __add_variations_to_gene(self, custom_report_variations: list, custom_report_gene: CustomReportGene) -> list:
        for variation in custom_report_variations:
            variation['custom_report_gene'] = custom_report_gene

        return custom_report_variations
