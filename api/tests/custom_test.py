from rest_framework import status

from api.tests.test import TestCase, data_provider
from api.models import CustomTest as CustomTestModel


class CustomTest(TestCase):
    fixtures = ['api/tests/fixtures/dumps/custom_test.json']

    def get_data_for_test_create(self):
        return (
            (
                '/custom_test/new_custom_test.json',
                status.HTTP_201_CREATED,
                '/custom_test/created_custom_test.json'
            ),
            (
                '/custom_test/new_custom_test_with_exists_patient.json',
                status.HTTP_201_CREATED,
                '/custom_test/created_custom_test_with_exists_patient.json'
            ),
            (
                '/custom_test/new_custom_test_without_patient.json',
                status.HTTP_201_CREATED,
                '/custom_test/created_custom_test_without_patient.json'
            ),
        )

    @data_provider(get_data_for_test_create)
    def test_create(self, create_fixture, response_status, response_fixture):
        new_custom_tests = self.load_fixture(create_fixture)

        self.force_login_user(1)
        response = self.client.post('/api/custom-tests/', new_custom_tests)

        self.assertEquals(response.status_code, response_status)
        self.assertEqualsFixture(response.data, response_fixture)

    def get_data_for_test_update(self):
        return (
            (
                '/custom_test/update_custom_test.json',
                status.HTTP_200_OK,
                '/custom_test/updated_custom_test.json'
            ),
            (
                '/custom_test/update_custom_test_with_null_patient.json',
                status.HTTP_200_OK,
                '/custom_test/updated_custom_test_with_null_patient.json'
            ),
            (
                '/custom_test/update_custom_test_without_patient.json',
                status.HTTP_200_OK,
                '/custom_test/updated_custom_test_without_patient.json'
            ),
            (
                '/custom_test/update_custom_test_by_exists_patient.json',
                status.HTTP_200_OK,
                '/custom_test/updated_custom_test_by_exists_patient.json'
            ),
        )

    @data_provider(get_data_for_test_update)
    def test_update(self, update_fixture, response_status, response_fixture):
        update_data = self.load_fixture(update_fixture)

        self.force_login_user(1)
        response = self.client.put('/api/custom-tests/1/', update_data)

        self.assertEquals(response.status_code, response_status)
        self.assertEqualsFixture(response.data, response_fixture)

    def test_delete(self):
        self.force_login_user(1)
        response = self.client.delete('/api/custom-tests/1/')

        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CustomTestModel.objects.filter(pk=1).exists())


    def test_get(self):
        self.force_login_user(1)
        response = self.client.get('/api/custom-tests/1/')

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEqualsFixture(response.data, '/custom_test/get_custom_test.json')

    def get_filters_for_user_search(self):
        return (
            (
                {'all': True},
                '/custom_test/get_all.json'
            ),
            (
                {'all': True, 'expand': ['custom_test_reports']},
                '/custom_test/get_all.json'
            ),
            (
                {'sort': ['name']},
                '/custom_test/get_all_with_name_sort.json'
            ),
            (
                {'sort': ['type']},
                '/custom_test/get_all_with_type_sort.json'
            ),
            (
                {'search': ['CustomReportTest2']},
                '/custom_test/get_all_searched.json'
            ),
        )

    @data_provider(get_filters_for_user_search)
    def test_search(self, filters, fixture):
        self.force_login_user(1)
        response = self.client.get('/api/custom-tests/', filters)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEqualsFixture(response.data, fixture )
