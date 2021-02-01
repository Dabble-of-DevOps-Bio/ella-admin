from django_filters import rest_framework

from api.models import CustomReportTest


class CustomReportTestFilter(rest_framework.FilterSet):
    sort = rest_framework.OrderingFilter(
        fields=(
            ('name', 'name'),
            ('type', 'type'),
        )
    )

    class Meta:
        model = CustomReportTest
        fields = ('name', 'type',)
