from rest_framework import status

from api.tests.test import TestCase, data_provider
from api.models import CustomTestReport as CustomTestReportModel


class CustomTestReport(TestCase):
    fixtures = ['api/tests/fixtures/dumps/custom_test_report.json']

    def get_data_for_test_create(self):
        return (
            (
                '/custom_test_report/create_custom_test_report.json',
                status.HTTP_201_CREATED,
                '/custom_test_report/created_custom_test_report.json'
            ),
            (
                '/custom_test_report/create_custom_test_report_with_only_required.json',
                status.HTTP_201_CREATED,
                '/custom_test_report/created_custom_test_report_with_only_required.json'
            ),
            (
                '/custom_test_report/create_custom_test_report_with_empty_fields.json',
                status.HTTP_201_CREATED,
                '/custom_test_report/created_custom_test_report_with_empty_fields.json'
            ),
            (
                '/custom_test_report/create_custom_test_report_without_custom_test_id.json',
                status.HTTP_400_BAD_REQUEST,
                '/custom_test_report/created_custom_test_report_without_custom_test_id.json'
            ),
            (
                '/custom_test_report/create_custom_test_report_with_not_existed_custom_test_id.json',
                status.HTTP_400_BAD_REQUEST,
                '/custom_test_report/created_custom_test_report_with_not_existed_custom_test_id.json'
            ),
        )

    @data_provider(get_data_for_test_create)
    def test_create(self, create_fixture, response_status, response_fixture):
        new_custom_test_report = self.load_fixture(create_fixture)

        self.force_login_user(1)
        response = self.client.post('/api/custom-test-reports/', new_custom_test_report)

        self.assertEquals(response.status_code, response_status)
        self.assertEqualsFixture(response.data, response_fixture)

    def test_update(self):
        update_data = self.load_fixture('/custom_test_report/update_custom_test_report.json')

        self.force_login_user(1)
        response = self.client.put('/api/custom-test-reports/1/', update_data)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEqualsFixture(response.data, '/custom_test_report/updated_custom_test_report.json')

    def test_delete(self):
        self.force_login_user(1)
        response = self.client.delete('/api/custom-test-reports/1/')

        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CustomTestReportModel.objects.filter(pk=1).exists())


    def test_get(self):
        self.force_login_user(1)
        response = self.client.get('/api/custom-test-reports/1/', {'expand': ['custom_test',
                                                                              'custom_test_report_genes.custom_test_gene',
                                                                              'custom_test_report_variations.custom_test_variation']})

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEqualsFixture(response.data, '/custom_test_report/get_custom_test_report.json')

    def get_data_for_test_search(self):
        return (
            (
                {'all': True},
                '/custom_test_report/get_all.json'
            ),
        )

    @data_provider(get_data_for_test_search)
    def test_search(self, filters, fixture):
        self.force_login_user(1)
        response = self.client.get('/api/custom-test-reports/', filters)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEqualsFixture(response.data, fixture)
