from django_filters import rest_framework

from api.models import Patient


class PatientFilter(rest_framework.FilterSet):
    sort = rest_framework.OrderingFilter(
        fields=(
            ('name', 'name'),
            ('birthday', 'birthday'),
            ('gender', 'gender'),
            ('sample_type', 'sample_type'),
            ('sample_id', 'sample_id'),
            ('test_accession', 'test_accession'),
            ('test_ordered', 'test_ordered'),
            ('test_code', 'test_code'),
            ('ordered_by', 'ordered_by'),
            ('sample_collection_date', 'sample_collection_date'),
            ('sample_accession_date', 'sample_accession_date'),
            ('report_date', 'report_date'),
        )
    )

    class Meta:
        model = Patient
        fields = ('name', 'birthday', 'gender', 'sample_type', 'sample_id',
            'test_accession', 'test_ordered', 'test_code', 'ordered_by',
            'sample_collection_date', 'sample_accession_date', 'report_date',)
