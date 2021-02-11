from rest_framework import status

from api.tests.test import TestCase, data_provider
from api.models import CustomTestVariation as CustomTestVariationModel


class CustomTestVariation(TestCase):
    fixtures = ['api/tests/fixtures/dumps/custom_test_variation.json']

    def get_data_for_test_create(self):
        return (
            (
                '/custom_test_variation/new_custom_test_variation.json',
                status.HTTP_201_CREATED,
                '/custom_test_variation/created_custom_test_variation.json',
            ),
        )

    @data_provider(get_data_for_test_create)
    def test_create(self, create_fixture, response_status, response_fixture):
        new_custom_test_gene = self.load_fixture(create_fixture)

        self.force_login_user(1)
        response = self.client.post('/api/custom-test-variations/', new_custom_test_gene)

        self.assertEquals(response.status_code, response_status)
        self.assertEqualsFixture(response.data, response_fixture)

    def get_data_for_test_update(self):
        return (
            (
                '/custom_test_variation/update_custom_test_variation.json',
                status.HTTP_200_OK,
                '/custom_test_variation/updated_custom_test_variation.json',
            ),
        )

    @data_provider(get_data_for_test_update)
    def test_update(self, update_fixture, response_status, response_fixture):
        update_data = self.load_fixture(update_fixture)

        self.force_login_user(1)
        response = self.client.put('/api/custom-test-variations/1/', update_data)

        self.assertEquals(response.status_code, response_status)
        self.assertEqualsFixture(response.data, response_fixture)

    def test_delete(self):
        self.force_login_user(1)
        response = self.client.delete('/api/custom-test-variations/1/')

        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CustomTestVariationModel.objects.filter(pk=1).exists())


    def test_get(self):
        self.force_login_user(1)
        response = self.client.get('/api/custom-test-variations/1/')

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEqualsFixture(response.data, '/custom_test_variation/get_custom_test_variation.json')

    def get_filters_for_user_search(self):
        return (
            (
                {'all': True},
                '/custom_test_variation/get_all.json'
            ),
            (
                {'sort': ['variation']},
                '/custom_test_variation/get_all_with_variation_sort.json'
            ),
            (
                {'sort': ['classification']},
                '/custom_test_variation/get_all_with_classification_sort.json'
            ),
            (
                {'sort': ['zygosity']},
                '/custom_test_variation/get_all_with_zygosity_sort.json'
            ),
            (
                {'search': ['BRCA2']},
                '/custom_test_variation/get_all_searched.json'
            ),
        )

    @data_provider(get_filters_for_user_search)
    def test_search(self, filters, fixture):
        self.force_login_user(1)
        response = self.client.get('/api/custom-test-variations/', filters)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEqualsFixture(response.data, fixture)
