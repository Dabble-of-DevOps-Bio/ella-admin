from rest_framework import status

from api.models.user_group import UserGroup
from api.tests.test import TestCase, data_provider


class UserGroupTest(TestCase):
    fixtures = ['api/tests/fixtures/dumps/user_group.json']

    def test_create(self):
        new_user_group = self.load_fixture('/user_group/new_user_group.json')

        self.force_login_user(1)
        response = self.client.post('/api/user-groups/', new_user_group)

        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEqualsFixture(response.data, '/user_group/created_user_group.json')

    def test_create_with_exists_name(self):
        new_user_group = self.load_fixture('/user_group/new_user_group_with_exists_name.json')

        self.force_login_user(1)
        response = self.client.post('/api/user-groups/', new_user_group)

        self.assertBadRequest(response)

    def test_create_by_staff(self):
        new_user_group = self.load_fixture('/user_group/new_user_group.json')

        self.force_login_user(2)
        response = self.client.post('/api/user-groups/', new_user_group)

        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_by_admin(self):
        update_data = self.load_fixture('/user_group/update_user_group.json')

        self.force_login_user(1)
        response = self.client.put('/api/user-groups/1/', update_data)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEqualsFixture(response.data, '/user_group/updated_user.json')

    def test_update_by_staff(self):
        update_data = self.load_fixture('/user_group/update_user_group.json')

        self.force_login_user(2)
        response = self.client.put('/api/user-groups/1/', update_data)

        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete(self):
        self.force_login_user(1)
        response = self.client.delete('/api/user-groups/1/')

        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(UserGroup.objects.filter(pk=1).exists())

    def test_delete_by_staff(self):
        self.force_login_user(2)
        response = self.client.delete('/api/user-groups/1/')

        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

    def get_filters_for_user_group_search(self):
        return (
            (
                {'all': True},
                '/user_group/get_all.json.json'
            ),
            (
                {'sort': 'name'},
                '/user_group/get_all_sorted_by_name.json'
            ),
        )

    @data_provider(get_filters_for_user_group_search)
    def test_search(self, filters, fixture):
        self.force_login_user(1)
        response = self.client.get('/api/user-groups/', filters)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEqualsFixture(response.data, fixture)

    def test_get(self):
        self.force_login_user(1)
        response = self.client.get('/api/user-groups/1/')

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEqualsFixture(response.data, '/user_group/get_user_group.json')

    def test_get_by_staff(self):
        self.force_login_user(2)
        response = self.client.get('/api/user-groups/1/')

        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)
