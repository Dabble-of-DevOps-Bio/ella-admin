from django_filters import rest_framework

from api.models import CustomTestGene


class CustomTestGeneFilter(rest_framework.FilterSet):
    sort = rest_framework.OrderingFilter(
        fields=(
            ('name', 'name'),
            ('transcript', 'transcript'),
        )
    )

    class Meta:
        model = CustomTestGene
        fields = ('name', 'transcript',)
