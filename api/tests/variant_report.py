from rest_framework import status

from api.tests.test import TestCase


class VariantReportTest(TestCase):
    fixtures = ['api/tests/fixtures/dumps/variant_report.json']

    def test_get(self):
        self.force_login_user(1)
        response = self.client.get('/api/analysis/7/variant-report/')

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEqualsFixture(response.data, '/variant_report/get_variant_report.json')

    def test_get_without_interpretation(self):
        self.force_login_user(1)
        response = self.client.get('/api/analysis/2/variant-report/')

        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_with_not_finalized_interpretation(self):
        self.force_login_user(1)
        response = self.client.get('/api/analysis/3/variant-report/')

        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_already_existed(self):
        self.force_login_user(1)
        response = self.client.get('/api/analysis/1/variant-report/')

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEqualsFixture(response.data, '/variant_report/get_already_existed_variant_report.json')

    def test_update(self):
        data = self.load_fixture('/variant_report/update_variant_report.json')

        self.force_login_user(1)
        response = self.client.put('/api/analysis/1/variant-report/', data)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEqualsFixture(response.data, '/variant_report/updated_variant_report.json')

    def test_update_by_not_valid_data(self):
        data = self.load_fixture('/variant_report/update_not_valid_variant_report.json')

        self.force_login_user(1)
        response = self.client.put('/api/analysis/1/variant-report/', data)

        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_by_data_with_unknown_field(self):
        data = self.load_fixture('/variant_report/update_by_variant_report_with_unknown_field.json')

        self.force_login_user(1)
        response = self.client.put('/api/analysis/1/variant-report/', data)

        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_not_existed(self):
        data = self.load_fixture('/variant_report/update_variant_report.json')

        self.force_login_user(1)
        response = self.client.put('/api/analysis/7/variant-report/', data)

        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_patient_data(self):
        self.force_login_user(1)
        response = self.client.get('/api/analysis/7/patient-data/')

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEqualsFixture(response.data, '/variant_report/get_patient_data.json')
