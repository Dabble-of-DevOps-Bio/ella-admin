from rest_framework import status

from api.tests.test import TestCase, data_provider
from api.models import CustomTestReport as CustomTestReportModel


class CustomTestReport(TestCase):
    fixtures = ['api/tests/fixtures/dumps/custom_test_report.json']

    def test_create(self):
        new_custom_test_report = self.load_fixture('/custom_test_report/new_custom_test_report.json')

        self.force_login_user(1)
        response = self.client.post('/api/custom-test-reports/', new_custom_test_report)

        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEqualsFixture(response.data, '/custom_test_report/created_custom_test_report.json', export=True)

    def test_update(self):
        update_data = self.load_fixture('/custom_test_report/update_custom_test_report.json')

        self.force_login_user(1)
        response = self.client.put('/api/custom-test-reports/1/', update_data)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEqualsFixture(response.data, '/custom_test_report/updated_custom_test_report.json', export=True)

    def test_delete(self):
        self.force_login_user(1)
        response = self.client.delete('/api/custom-test-reports/1/')

        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CustomTestReportModel.objects.filter(pk=1).exists())


    def test_get(self):
        self.force_login_user(1)
        response = self.client.get('/api/custom-test-reports/1/')

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEqualsFixture(response.data, '/custom_test_report/get_custom_test_report.json', export=True)

    def get_filters_for_user_search(self):
        return (
            (
                {'all': True},
                '/custom_test_report/get_all.json'
            ),
        )

    @data_provider(get_filters_for_user_search)
    def test_search(self, filters, fixture):
        self.force_login_user(1)
        response = self.client.get('/api/custom-test-reports/', filters)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEqualsFixture(response.data, fixture, export=True)
