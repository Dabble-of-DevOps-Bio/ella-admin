import pydash

from rest_framework.fields import IntegerField, CharField

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.http.serializers.custom_report_interpretation_serializer import CustomReportInterpretationSerializer
from api.http.validators import ExistsValidator
from api.models import CustomReportResult


class CustomReportResultSerializer(BaseModelSerializer):
    class Meta:
        model = CustomReportResult
        fields = (
            'id', 'result', 'custom_report_interpretation'
        )

    id = IntegerField(required=False, validators=[ExistsValidator(queryset=CustomReportResult.objects.all())])
    result = CharField()
    custom_report_interpretation = CustomReportInterpretationSerializer(source='customreportinterpretation', required=False)

    def create(self, validated_data):
        custom_report_interpretation = None
        if 'customreportinterpretation' in validated_data:
            custom_report_interpretation = validated_data.pop('customreportinterpretation')

        custom_report_result = CustomReportResult(**validated_data)

        custom_report_result.save()

        if custom_report_interpretation is not None:
            self.__create_custom_report_interpretation(custom_report_interpretation, custom_report_result)

        return custom_report_result

    def update(self, instance: CustomReportResult, validated_data):
        if 'customreportinterpretation' in validated_data:
            custom_report_interpretations = validated_data.pop('customreportinterpretation')

            if 'id' in custom_report_interpretations:
                self.__update_custom_report_interpretation(custom_report_interpretations, instance)
            else:
                self.__create_custom_report_interpretation(custom_report_interpretations, instance)

        return super().update(instance, validated_data)

    def __create_custom_report_interpretation(self, custom_report_interpretation, custom_report_result: CustomReportResult) -> None:
        if pydash.get(custom_report_result, 'customreportinterpretation') is not None:
            custom_report_result.customreportinterpretation.delete()

        custom_report_interpretation_serializer = CustomReportInterpretationSerializer()
        custom_report_interpretation['custom_report_result'] = custom_report_result

        custom_report_interpretation_serializer.create(custom_report_interpretation)

    def __update_custom_report_interpretation(self, custom_report_interpretation, custom_report_result: CustomReportResult) -> None:
        custom_report_interpretation_serializer = CustomReportInterpretationSerializer()
        custom_report_interpretation_serializer.update(custom_report_result.customreportinterpretation, custom_report_interpretation)
