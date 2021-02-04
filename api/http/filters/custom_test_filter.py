from django_filters import rest_framework

from api.models import CustomTest


class CustomTestFilter(rest_framework.FilterSet):
    sort = rest_framework.OrderingFilter(
        fields=(
            ('name', 'name'),
            ('type', 'type'),
        )
    )

    class Meta:
        model = CustomTest
        fields = ('name', 'type',)
