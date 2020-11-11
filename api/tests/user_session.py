from api.tests.test import TestCase
from api.models import UserSession


class UserSessionTest(TestCase):
    fixtures = ['api/tests/fixtures/dumps/user_session.json']

    def test_create(self):
        self.force_login_user(1)
        response = self.client.post('/api/staff-app-login/')

        self.assertOk(response)

        self.assertEqual(UserSession.objects.all().count(), 1)

        self.assertIsNotNone(response.cookies['AuthenticationToken'])
        self.assertEqual(response.cookies['AuthenticationToken']['path'], '/')
        self.assertEqual(response.cookies['AuthenticationToken']['domain'], 'localhost')
        self.assertTrue(response.cookies['AuthenticationToken']['httponly'])
        self.assertIsNotNone(response.cookies['AuthenticationToken']['expires'])
