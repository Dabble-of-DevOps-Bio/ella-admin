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

    only_finalized = rest_framework.BooleanFilter(method='filter_by_only_finalized')

    def filter_by_only_finalized(self, queryset, value, name):
        if value:
            return queryset.filter(analysisinterpretation__finalized=True)

        return queryset

    class Meta:
        model = Analysis
        fields = ('name', 'gene_panel_name', 'gene_panel_version',)
