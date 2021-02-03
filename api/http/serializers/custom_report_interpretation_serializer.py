from rest_framework.fields import IntegerField, CharField

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import CustomReportInterpretation
from api.http.validators import ExistsValidator

class CustomReportInterpretationSerializer(BaseModelSerializer):
    class Meta:
        model = CustomReportInterpretation
        fields = (
            'id', 'interpretations',
        )

    id = IntegerField(required=False, validators=[ExistsValidator(queryset=CustomReportInterpretation.objects.all())])

    interpretations = CharField()
