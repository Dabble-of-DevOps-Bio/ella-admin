from rest_framework.fields import ReadOnlyField, CharField, ChoiceField

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.http.serializers.custom_test_gene_serializer import CustomTestGeneSerializer
from api.http.serializers.patient_serializer import PatientSerializer
from api.models import CustomTest, Patient


class CustomTestSerializer(BaseModelSerializer):
    class Meta:
        model = CustomTest
        fields = (
            'id', 'name', 'type', 'finding', 'methodology', 'limitations', 'references', 'patient',
            'custom_test_genes', 'created_at', 'updated_at',
        )
        expandable_fields = {
            'patient': (PatientSerializer,),
            'custom_test_reports': ('api.http.serializers.CustomTestReportSerializer', {'source': 'customtestreport_set', 'many': True}),
        }

    id = ReadOnlyField()

    name = CharField()

    type = ChoiceField(choices=CustomTest.Type.choices)
    finding = ChoiceField(choices=CustomTest.Finding.choices)

    methodology = CharField(required=False)
    limitations = CharField(required=False)
    references = CharField(required=False)

    patient = PatientSerializer(required=False, allow_null=True)

    custom_test_genes = CustomTestGeneSerializer(source='customtestgene_set', required=False, many=True)

    def create(self, validated_data):
        custom_test_genes = None
        if 'customtestgene_set' in validated_data:
            custom_test_genes = validated_data.pop('customtestgene_set')

        self.__create_or_update_patient(validated_data)

        custom_test = CustomTest(**validated_data)
        custom_test.save()

        if custom_test_genes is not None:
            self.__create_custom_test_genes(custom_test_genes, custom_test)

        return custom_test

    def update(self, instance: CustomTest, validated_data):
        custom_test_genes = None
        if 'customtestgene_set' in validated_data:
            custom_test_genes = validated_data.pop('customtestgene_set')

        self.__sync_custom_test_genes(custom_test_genes, instance)

        self.__create_or_update_patient(validated_data)

        return super().update(instance, validated_data)

    def __create_custom_test_genes(self, custom_test_genes: list, custom_test: CustomTest) -> None:
        if custom_test_genes is not None and len(custom_test_genes) > 0:
            custom_report_gene_serializer = CustomTestGeneSerializer()
            custom_report_gene_serializer.bulk_create(custom_test_genes, custom_test)

    def __update_custom_test_genes(self, custom_test_genes: list) -> None:
        if custom_test_genes is not None and len(custom_test_genes) > 0:
            custom_report_gene_serializer = CustomTestGeneSerializer()
            custom_report_gene_serializer.bulk_update(custom_test_genes)

    def __create_or_update_patient(self, custom_test_data: dict):
        if 'patient' in custom_test_data and custom_test_data['patient'] is not None:
            if 'id' in custom_test_data['patient']:
                custom_test_data['patient'] = self.__update_patient(custom_test_data['patient'])
            else:
                custom_test_data['patient'] = self.__create_patient(custom_test_data['patient'])

    def __create_patient(self, patient_data: dict) -> Patient:
        patient_serializer = PatientSerializer()
        patient = patient_serializer.create(patient_data)
        patient.save()

        return patient

    def __update_patient(self, patient_data: dict) -> Patient:
        patient = Patient.objects.get(pk=patient_data['id'])

        patient_serializer = PatientSerializer()
        patient_serializer.update(patient, patient_data)

        patient.refresh_from_db()

        return patient

    def __sync_custom_test_genes(self, custom_test_genes: list, custom_test: CustomTest) -> None:
        if custom_test_genes is not None:
            self.__remove_not_existed_genes(custom_test_genes, custom_test)

            new_genes, existed_genes = self._divide_data(custom_test_genes)

            self.__create_custom_test_genes(new_genes, custom_test)
            self.__update_custom_test_genes(existed_genes)

    def __remove_not_existed_genes(self, custom_test_genes: list, custom_test: CustomTest):
        existing_ids = [entity['id'] for entity in custom_test_genes if 'id' in entity]

        custom_test.customtestgene_set.exclude(pk__in=existing_ids).delete()
