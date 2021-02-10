from rest_framework import status

from api.tests.test import TestCase, data_provider
from api.models import Patient


class PatientTest(TestCase):
    fixtures = ['api/tests/fixtures/dumps/patient.json']

    def test_create(self):
        new_patients = self.load_fixture('/patient/new_patient.json')

        self.force_login_user(1)
        response = self.client.post('/api/patients/', new_patients)

        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEqualsFixture(response.data, '/patient/created_patient.json')

    def test_update(self):
        update_data = self.load_fixture('/patient/update_patient.json')

        self.force_login_user(1)
        response = self.client.put('/api/patients/1/', update_data)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEqualsFixture(response.data, '/patient/updated_patient.json')

    def test_delete(self):
        self.force_login_user(1)
        response = self.client.delete('/api/patients/1/')

        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Patient.objects.filter(pk=1).exists())

    def test_get(self):
        self.force_login_user(1)
        response = self.client.get('/api/patients/1/')

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEqualsFixture(response.data, '/patient/get_patient.json')

    def get_filters_for_user_search(self):
        return (
            (
                {'all': True},
                '/patient/get_all.json'
            ),
            (
                {'sort': ['name']},
                '/patient/get_all_with_name_sort.json'
            ),
            (
                {'search': ['Todd']},
                '/patient/get_all_searched.json'
            ),
        )

    @data_provider(get_filters_for_user_search)
    def test_search(self, filters, fixture):
        self.force_login_user(1)
        response = self.client.get('/api/patients/', filters)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEqualsFixture(response.data, fixture)
