from rest_framework import status

from api.tests.test import TestCase, data_provider


class AnalysisTest(TestCase):
    fixtures = ['api/tests/fixtures/dumps/analysis.json']

    def get_filters_for_analysis_search(self):
        return (
            (
                {'all': True},
                '/analysis/get_all.json'
            ),
            (
                {'sort': 'name'},
                '/analysis/get_all_sorted_by_name.json'
            ),
            (
                {'sort': 'gene_panel_name'},
                '/analysis/get_all_sorted_by_gene_panel_name.json'
            ),
            (
                {'sort': 'gene_panel_version'},
                '/analysis/get_all_sorted_by_gene_panel_version.json'
            ),
            (
                {'search': 'brca_long'},
                '/analysis/get_all_search_by_name.json'
            ),
            (
                {'search': 'HBOC'},
                '/analysis/get_all_search_by_gene_panel_name.json'
            ),
            (
                {'search': 'v02'},
                '/analysis/get_all_search_by_gene_panel_version.json'
            ),
        )

    @data_provider(get_filters_for_analysis_search)
    def test_search(self, filters, fixture):
        self.force_login_user(1)
        response = self.client.get('/api/analysis/', filters)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEqualsFixture(response.data, fixture)

    def test_get(self):
        self.force_login_user(1)
        response = self.client.get('/api/analysis/1/')

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEqualsFixture(response.data, '/analysis/get_analysis.json')
