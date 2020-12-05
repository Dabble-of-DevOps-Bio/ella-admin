from rest_framework import status

from api.tests.test import TestCase, data_provider


class GenePanelTest(TestCase):
    fixtures = ['api/tests/fixtures/dumps/gene_panel.json']

    def get_filters_for_user_search(self):
        return (
            (
                {'all': True},
                '/gene_panel/get_all.json'
            ),
            (
                {'expand': ['groups']},
                '/gene_panel/get_all_with_expand_groups.json'
            ),
            (
                {'sort': ['name']},
                '/gene_panel/get_all_with_name_sort.json'
            ),
            (
                {'sort': ['version']},
                '/gene_panel/get_all_with_version_sort.json'
            ),
            (
                {'search': ['v01']},
                '/gene_panel/get_all_searched.json'
            ),
        )

    @data_provider(get_filters_for_user_search)
    def test_search(self, filters, fixture):
        self.force_login_user(1)
        response = self.client.get('/api/gene-panels/', filters)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEqualsFixture(response.data, fixture)


    def get_filters_for_test_get_gene_panel(self):
        return (
            (
                {},
                '/gene_panel/get_gene_panel.json'
            ),
            (
                {'expand': ['groups']},
                '/gene_panel/get_gene_panel_with_expand_groups.json'
            ),
        )

    @data_provider(get_filters_for_test_get_gene_panel)
    def test_get(self, filters, fixture):
        self.force_login_user(1)
        response = self.client.get('/api/gene-panels/1/', filters)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEqualsFixture(response.data, fixture)

    def test_update(self):
        update_data = self.load_fixture('/gene_panel/update.json')

        self.force_login_user(1)
        response = self.client.put('/api/gene-panels/1/', update_data)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEqualsFixture(response.data, '/gene_panel/updated.json')

    def get_data_for_test_get_update_groups(self):
        return (
            (
                {
                    'gene_panel_id': 3,
                    'fixture_path': '/gene_panel/add_groups_to_empty.json',
                },
                {
                    'response_status': status.HTTP_200_OK,
                    'fixture_path': '/gene_panel/added_groups_to_empty.json'
                }

            ),
            (
                {
                    'gene_panel_id': 1,
                    'fixture_path': '/gene_panel/update_groups.json',
                },
                {
                    'response_status': status.HTTP_200_OK,
                    'fixture_path': '/gene_panel/updated_groups.json'
                }
            ),
            (
                {
                    'gene_panel_id': 1,
                    'fixture_path': '/gene_panel/update_by_same_groups.json',
                },
                {
                    'response_status': status.HTTP_200_OK,
                    'fixture_path': '/gene_panel/updated_by_same_groups.json'
                }
            ),
            (
                {
                    'gene_panel_id': 1,
                    'fixture_path': '/gene_panel/clear_groups.json'
                },
                {
                    'response_status': status.HTTP_200_OK,
                    'fixture_path': '/gene_panel/cleared_groups.json'
                }
            ),
            (
                {
                    'gene_panel_id': 1,
                    'fixture_path': '/gene_panel/add_incorrect_groups.json',
                },
                {
                    'response_status': status.HTTP_400_BAD_REQUEST,
                    'fixture_path': None
                }
            )
        )

    @data_provider(get_data_for_test_get_update_groups)
    def test_update_groups(self, update_data, result_data):
        data = self.load_fixture(update_data['fixture_path'])

        self.force_login_user(1)
        response = self.client.put('/api/gene-panels/%s/' % update_data['gene_panel_id'], data)

        self.assertEquals(response.status_code, result_data['response_status'])
        if result_data['fixture_path'] is not None:
            self.assertEqualsFixture(response.data, result_data['fixture_path'])
