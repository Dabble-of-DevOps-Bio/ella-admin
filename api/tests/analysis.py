from rest_framework import status

from api.tests.test import TestCase, data_provider


class AnalysisTest(TestCase):
    fixtures = ['api/tests/fixtures/dumps/analysis.json']

    def get_filters_for_test_search(self):
        return (
            (
                {
                    'filters': {'all': True},
                    'user_id': 2
                },
                '/analysis/get_all.json'
            ),
            (
                {
                    'filters': {'sort': 'name'},
                    'user_id': 2
                },
                '/analysis/get_all_sorted_by_name.json'
            ),
            (
                {
                    'filters': {'sort': 'gene_panel_name'},
                    'user_id': 2
                },
                '/analysis/get_all_sorted_by_gene_panel_name.json'
            ),
            (
                {
                    'filters': {'sort': 'gene_panel_version'},
                    'user_id': 2
                },
                '/analysis/get_all_sorted_by_gene_panel_version.json'
            ),
            (
                {
                    'filters': {'search': 'brca_long'},
                    'user_id': 2
                },
                '/analysis/get_all_search_by_name.json'
            ),
            (
                {
                    'filters': {'search': 'HBOC'},
                    'user_id': 2
                },
                '/analysis/get_all_search_by_gene_panel_name.json'
            ),
            (
                {
                    'filters': {'search': 'v02'},
                    'user_id': 2
                },
                '/analysis/get_all_search_by_gene_panel_version.json'
            ),
            (
                {
                    'filters': {'all': True},
                    'user_id': 1
                },
                '/analysis/get_all_related_to_user.json'
            ),
            (
                {
                    'filters': {'all': True, 'only_finalized': True},
                    'user_id': 1
                },
                '/analysis/get_filtered_by_only_finalized.json'
            ),
            (
                {
                    'filters': {'all': True, 'only_finalized': True},
                    'user_id': 2
                },
                '/analysis/get_filtered_by_only_finalized_for_second_user.json'
            ),
        )

    @data_provider(get_filters_for_test_search)
    def test_search(self, update_date, fixture):
        self.force_login_user(update_date['user_id'])
        response = self.client.get('/api/analysis/', update_date['filters'])

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEqualsFixture(response.data, fixture)

    def test_get(self):
        self.force_login_user(1)
        response = self.client.get('/api/analysis/1/')

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEqualsFixture(response.data, '/analysis/get_analysis.json')
