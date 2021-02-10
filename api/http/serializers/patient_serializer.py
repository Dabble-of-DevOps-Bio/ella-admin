from rest_framework.fields import IntegerField, CharField, ChoiceField, DateField, DateTimeField

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.http.validators import ExistsValidator
from api.models import Patient


class PatientSerializer(BaseModelSerializer):
    class Meta:
        model = Patient
        fields = (
            'id', 'name', 'birthday', 'gender', 'sample_type', 'sample_id',
            'test_accession', 'test_ordered', 'test_code', 'ordered_by',
            'sample_collection_date', 'sample_accession_date', 'report_date',
        )

    id = IntegerField(required=False, validators=[ExistsValidator(queryset=Patient.objects.all())])

    name = CharField()
    birthday = DateField()
    gender = ChoiceField(choices=Patient.Gender.choices)

    sample_type = CharField(required=False, allow_blank=True)
    sample_id = CharField(required=False, allow_blank=True)

    test_accession = CharField(required=False, allow_blank=True)
    test_ordered = CharField(required=False, allow_blank=True)
    test_code = CharField(required=False, allow_blank=True)

    ordered_by = CharField(required=False, allow_blank=True)

    sample_collection_date = DateTimeField(required=False)
    sample_accession_date = DateTimeField(required=False)
    report_date = DateTimeField(required=False)
