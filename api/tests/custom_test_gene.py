from rest_framework import status

from api.tests.test import TestCase, data_provider
from api.models import CustomTestGene as CustomTestGeneModel


class CustomTestGene(TestCase):
    fixtures = ['api/tests/fixtures/dumps/custom_test_gene.json']

    def get_data_for_test_create(self):
        return (
            (
                '/custom_test_gene/new_custom_test_gene.json',
                status.HTTP_201_CREATED,
                '/custom_test_gene/created_custom_test_gene.json',
            ),
        )

    @data_provider(get_data_for_test_create)
    def test_create(self, create_fixture, response_status, response_fixture):
        new_custom_test_gene = self.load_fixture(create_fixture)

        self.force_login_user(1)
        response = self.client.post('/api/custom-test-genes/', new_custom_test_gene)

        self.assertEquals(response.status_code, response_status)
        self.assertEqualsFixture(response.data, response_fixture)

    def get_data_for_test_update(self):
        return (
            (
                '/custom_test_gene/update_custom_test_gene.json',
                status.HTTP_200_OK,
                '/custom_test_gene/updated_custom_test_gene.json',
            ),
        )

    @data_provider(get_data_for_test_update)
    def test_update(self, update_fixture, response_status, response_fixture):
        update_data = self.load_fixture(update_fixture)

        self.force_login_user(1)
        response = self.client.put('/api/custom-test-genes/1/', update_data)

        self.assertEquals(response.status_code, response_status)
        self.assertEqualsFixture(response.data, response_fixture)

    def test_delete(self):
        self.force_login_user(1)
        response = self.client.delete('/api/custom-test-genes/1/')

        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CustomTestGeneModel.objects.filter(pk=1).exists())


    def test_get(self):
        self.force_login_user(1)
        response = self.client.get('/api/custom-test-genes/1/')

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEqualsFixture(response.data, '/custom_test_gene/get_custom_test_gene.json')

    def get_filters_for_user_search(self):
        return (
            (
                {'all': True},
                '/custom_test_gene/get_all.json'
            ),
            (
                {'sort': ['name']},
                '/custom_test_gene/get_all_with_name_sort.json'
            ),
            (
                {'sort': ['transcript']},
                '/custom_test_gene/get_all_with_transcript_sort.json'
            ),
            (
                {'search': ['BRCA2']},
                '/custom_test_gene/get_all_searched.json'
            ),
        )

    @data_provider(get_filters_for_user_search)
    def test_search(self, filters, fixture):
        self.force_login_user(1)
        response = self.client.get('/api/custom-test-genes/', filters)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEqualsFixture(response.data, fixture)
