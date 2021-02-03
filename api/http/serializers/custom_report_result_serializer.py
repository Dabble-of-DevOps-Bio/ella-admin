from rest_framework.fields import IntegerField, CharField, ChoiceField

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.http.validators import ExistsValidator
from api.models import CustomReportResult


class CustomReportResultSerializer(BaseModelSerializer):
    class Meta:
        model = CustomReportResult
        fields = (
            'id', 'result', 'finding',
        )

    id = IntegerField(required=False, validators=[ExistsValidator(queryset=CustomReportResult.objects.all())])
    result = CharField()
    finding = ChoiceField(choices=CustomReportResult.Finding.choices)
