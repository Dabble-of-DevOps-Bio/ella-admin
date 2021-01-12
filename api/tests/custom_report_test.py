from rest_framework import status

from api.tests.test import TestCase, data_provider
from api.models import CustomReportTest as CustomReportTestModel


class CustomReportTest(TestCase):
    fixtures = ['api/tests/fixtures/dumps/custom_report_test.json']

    def test_create(self):
        new_custom_report_tests = self.load_fixture('/custom_report_test/new_custom_report_test.json')

        self.force_login_user(1)
        response = self.client.post('/api/custom-report-tests/', new_custom_report_tests)

        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEqualsFixture(response.data, '/custom_report_test/created_custom_report_test.json')

    def test_update(self):
        update_data = self.load_fixture('/custom_report_test/update_custom_report_test.json')

        self.force_login_user(1)
        response = self.client.put('/api/custom-report-tests/1/', update_data)

        self.assertEquals(response.status_code, status.HTTP_200_OK)

        response = self.client.get('/api/custom-report-tests/1/')
        self.assertEqualsFixture(response.data, '/custom_report_test/updated_custom_report_test.json')

    def test_delete(self):
        self.force_login_user(1)
        response = self.client.delete('/api/custom-report-tests/1/')

        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CustomReportTestModel.objects.filter(pk=1).exists())


    def test_get(self):
        self.force_login_user(1)
        response = self.client.get('/api/custom-report-tests/1/')

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEqualsFixture(response.data, '/custom_report_test/get_custom_report_test.json')

    def get_filters_for_user_search(self):
        return (
            (
                {'all': True},
                '/custom_report_test/get_all.json'
            ),
            (
                {'sort': ['name']},
                '/custom_report_test/get_all_with_name_sort.json'
            ),
            (
                {'sort': ['type']},
                '/custom_report_test/get_all_with_type_sort.json'
            ),
            (
                {'search': ['CustomReportTest2']},
                '/custom_report_test/get_all_searched.json'
            ),
        )

    @data_provider(get_filters_for_user_search)
    def test_search(self, filters, fixture):
        self.force_login_user(1)
        response = self.client.get('/api/custom-report-tests/', filters)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEqualsFixture(response.data, fixture)
