from django_filters import rest_framework

from api.models import Analysis


class AnalysisFilter(rest_framework.FilterSet):
    sort = rest_framework.OrderingFilter(
        fields=(
            ('name', 'name'),
            ('gene_panel_name', 'gene_panel_name'),
            ('gene_panel_version', 'gene_panel_version'),
        )
    )


    class Meta:
        model = Analysis
        fields = ('name', 'gene_panel_name', 'gene_panel_version',)
