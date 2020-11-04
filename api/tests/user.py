from unittest import mock

from django_rest_passwordreset.models import ResetPasswordToken
from rest_framework import status

from api.models import User
from api.tests.test import TestCase, data_provider


class UserTest(TestCase):
    fixtures = ['api/tests/fixtures/dumps/user.json']

    def mock_generate_token(self):
        return 123

    @mock.patch('django_rest_passwordreset.tokens.RandomStringTokenGenerator.generate_token', mock_generate_token)
    def test_create(self):
        new_user = self.load_fixture('/user/new_user.json')

        self.force_login_user(1)
        response = self.client.post('/api/users/', new_user)

        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEqualsFixture(response.data, '/user/created_user.json')
        self.assertTrue(User.objects.filter(pk=9, auth_groups__in=[2], is_superuser=False, is_staff=True).exists())
        self.assertTrue(ResetPasswordToken.objects.filter(user_id=9).exists())
        self.assertEmailEquals([
            {
                'to': ['mya-ferrell@mail.com'],
                'from_email': 'some_email@email.com',
                'fixture': self.responses_fixtures_dir + '/user/set_password.html'
            }
        ])

    def test_create_with_already_deleted_email(self):
        new_user = self.load_fixture('/user/new_user.json')
        new_user['email'] = "callen-burns@mail.com"

        self.force_login_user(1)
        response = self.client.post('/api/users/', new_user)

        self.assertBadRequest(response)

    def test_create_with_already_deleted_username(self):
        new_user = self.load_fixture('/user/new_user.json')
        new_user['username'] = "bronte-mccartney"

        self.force_login_user(1)
        response = self.client.post('/api/users/', new_user)

        self.assertBadRequest(response)

    def test_create_by_staff(self):
        new_user = self.load_fixture('/user/new_user.json')

        self.force_login_user(4)
        response = self.client.post('/api/users/', new_user)

        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

    @mock.patch('django_rest_passwordreset.tokens.RandomStringTokenGenerator.generate_token', mock_generate_token)
    def test_create_with_non_existing_group(self):
        new_user = self.load_fixture('/user/new_user_with_non_existing_group.json')

        self.force_login_user(1)
        response = self.client.post('/api/users/', new_user)

        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_by_admin(self):
        update_data = self.load_fixture('/user/update_user.json')

        self.force_login_user(1)
        response = self.client.put('/api/users/1/', update_data)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEqualsFixture(response.data, '/user/updated_user.json')

    def test_update_self_profile(self):
        update_data = self.load_fixture('/user/update_user.json')

        self.force_login_user(1)
        response = self.client.put('/api/profile/', update_data)

        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEquals(User.objects.get(pk=1).first_name, 'Eileen')
        self.assertEquals(User.objects.get(pk=1).last_name, 'Mill')

    def test_update_by_staff(self):
        update_data = self.load_fixture('/user/update_user.json')

        self.force_login_user(4)
        response = self.client.put('/api/users/2/', update_data)

        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete(self):
        self.force_login_user(1)
        response = self.client.delete('/api/users/4/')

        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertSoftDeleted(User, 4)

    def test_delete_by_staff(self):
        self.force_login_user(4)
        response = self.client.delete('/api/users/1/')

        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

    def get_filters_for_user_search(self):
        return (
            (
                {'sort': 'username'},
                '/user/get_all_sorted_by_username.json'
            ),
            (
                {'sort': 'email'},
                '/user/get_all_sorted_by_email.json'
            ),
            (
                {'sort': 'last_name'},
                '/user/get_all_sorted_by_last_name.json'
            ),
            (
                {'sort': 'first_name'},
                '/user/get_all_sorted_by_first_name.json'
            ),
        )

    @data_provider(get_filters_for_user_search)
    def test_search_by_superuser(self, filters, fixture):
        self.force_login_user(1)
        response = self.client.get('/api/users/', filters)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEqualsFixture(response.data, fixture, export=True)

    def test_get_by_superuser(self):
        self.force_login_user(1)
        response = self.client.get('/api/users/1/')

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEqualsFixture(response.data, '/user/get_user.json', export=True)

    def test_get_self_profile(self):
        self.force_login_user(1)
        response = self.client.get('/api/profile/')

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEqualsFixture(response.data, '/user/get_user.json')

    def test_get_forbidden(self):
        self.force_login_user(4)
        response = self.client.get('/api/users/2/')

        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

    @mock.patch('django_rest_passwordreset.tokens.RandomStringTokenGenerator.generate_token', mock_generate_token)
    def test_password_reset(self):
        response = self.client.post('/api/password-reset/', {'email': 'zaynab-barker@mail.com'})

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEmailEquals([
            {
                'from_email': 'some_email@email.com',
                'to': ['zaynab-barker@mail.com'],
                'fixture': self.responses_fixtures_dir + '/user/password_reset.html'
            }
        ])

    def test_update_password(self):
        user_update = self.load_fixture('/user/update_user_password.json')

        self.force_login_user(1)
        response = self.client.put('/api/profile/', user_update)
        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertTrue(User.objects.get(pk=1).check_password('123456Q#'))

    def test_update_password_without_new_password(self):
        user_update = self.load_fixture('/user/update_user_password.json')
        del user_update['new_password']

        self.force_login_user(1)
        response = self.client.put('/api/profile/', user_update)

        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_password_without_password(self):
        user_update = self.load_fixture('/user/update_user_password.json')
        del user_update['password']

        self.force_login_user(1)
        response = self.client.put('/api/profile/', user_update)

        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_password_with_invalid_password(self):
        user_update = self.load_fixture('/user/update_user_password.json')
        user_update['password'] = '235432dfsd'

        self.force_login_user(1)
        response = self.client.put('/api/profile/', user_update)

        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_password_with_the_same_password(self):
        user_update = self.load_fixture('/user/update_user_password.json')
        user_update['new_password'] = '123456Qwe-'

        self.force_login_user(1)
        response = self.client.put('/api/profile/', user_update)

        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
