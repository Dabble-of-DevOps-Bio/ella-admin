from django_filters import rest_framework

from api.models import CustomTestReport


class CustomTestReportFilter(rest_framework.FilterSet):
    sort = rest_framework.OrderingFilter(
        fields=()
    )

    class Meta:
        model = CustomTestReport
        fields = ()
