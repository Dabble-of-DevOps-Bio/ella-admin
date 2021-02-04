from rest_framework import status

from api.tests.test import TestCase, data_provider
from api.models import CustomTest as CustomReportTestModel


class CustomTest(TestCase):
    fixtures = ['api/tests/fixtures/dumps/custom_test.json']

    def test_create(self):
        new_custom_tests = self.load_fixture('/custom_test/new_custom_test.json')

        self.force_login_user(1)
        response = self.client.post('/api/custom-tests/', new_custom_tests)

        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEqualsFixture(response.data, '/custom_test/created_custom_test.json', export=True)

    def test_update(self):
        update_data = self.load_fixture('/custom_test/update_custom_test.json')

        self.force_login_user(1)
        response = self.client.put('/api/custom-tests/1/', update_data)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEqualsFixture(response.data, '/custom_test/updated_custom_test.json', export=True)

    def test_delete(self):
        self.force_login_user(1)
        response = self.client.delete('/api/custom-tests/1/')

        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CustomReportTestModel.objects.filter(pk=1).exists())


    def test_get(self):
        self.force_login_user(1)
        response = self.client.get('/api/custom-tests/1/')

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEqualsFixture(response.data, '/custom_test/get_custom_test.json', export=True)

    def get_filters_for_user_search(self):
        return (
            (
                {'all': True},
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
        self.assertEqualsFixture(response.data, fixture, export=True)
