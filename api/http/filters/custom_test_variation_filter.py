from django_filters import rest_framework

from api.models import CustomTestVariation


class CustomTestVariationFilter(rest_framework.FilterSet):
    sort = rest_framework.OrderingFilter(
        fields=(
            ('variation', 'variation'),
            ('classification', 'classification'),
            ('zygosity', 'zygosity'),
        )
    )

    class Meta:
        model = CustomTestVariation
        fields = ('variation', 'classification', 'zygosity',)
