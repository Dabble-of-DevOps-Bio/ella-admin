from django_filters import rest_framework

from api.models import GenePanel


class GenePanelFilter(rest_framework.FilterSet):
    sort = rest_framework.OrderingFilter(
        fields=(
            ('name', 'name'),
            ('version', 'version'),
        )
    )

    class Meta:
        model = GenePanel
        fields = ('name', 'version',)
