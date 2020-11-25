from api.tests.test import TestCase
from api.models import UserSession
from rest_framework import status


class UserSessionTest(TestCase):
    fixtures = ['api/tests/fixtures/dumps/user_session.json']

    def test_create(self):
        self.force_login_user(1)
        response = self.client.post('/api/staff-app-login/')

        self.assertEquals(response.status_code, status.HTTP_302_FOUND)

        self.assertEqual(UserSession.objects.all().count(), 1)

        self.assertIsNotNone(response.cookies['AuthenticationToken'])
        self.assertEqual(response.cookies['AuthenticationToken']['path'], '/')
        self.assertEqual(response.cookies['AuthenticationToken']['domain'], '.ronasit.')
        self.assertTrue(response.cookies['AuthenticationToken']['httponly'])
        self.assertIsNotNone(response.cookies['AuthenticationToken']['expires'])
