import json
from io import BytesIO

from PIL import Image
from django.core import mail
from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import User
from api.utilities.tests_helpers import load_fixture, load_json


def data_provider(data_provider_function):
    def wrapped_test(test_function):
        def call_wrapped_test_with_provided_data(self):
            for data in data_provider_function(self):
                test_function(self, *data)

        return call_wrapped_test_with_provided_data

    return wrapped_test


class TestCase(APITestCase):
    pass

    responses_fixtures_dir = 'api/tests/fixtures/responses'
    dumps_fixtures_dir = 'api/tests/fixtures/dumps'
    requests_fixtures_dir = 'api/tests/fixtures/requests'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self) -> None:
        self.frozen_time = freeze_time('2020-02-02')
        self.frozen_time.start()
        super().setUp()

    def tearDown(self) -> None:
        self.frozen_time.stop()
        super().tearDown()

    def force_login_user(self, value, field='pk'):
        user = User.objects.get(**{field: value})
        self.client.force_login(user)

    def load_fixture(self, local_path):
        return load_json(self.requests_fixtures_dir + local_path)

    def save_fixture(self, data, path):
        with open(path, 'w') as f:
            json.dump(data, f, indent=True)

    def save_bytes_fixture(self, path, data):
        f = open(path, 'wb')
        f.write(data)
        f.close()

    def assertEmailEquals(self, emails):
        sent_emails = mail.outbox
        for index, sent_email in enumerate(sent_emails):
            from_email = emails[index]['from_email']
            to_email = emails[index]['to']
            fixture = emails[index]['fixture']
            rendered_email = load_fixture(fixture)

            self.assertEquals(sent_email.from_email, from_email)
            self.assertEquals(sent_email.to, to_email)
            self.assertEquals(sent_email.body, rendered_email)

    def assertSoftDeleted(self, model_class, pk: int):
        self.assertTrue(model_class.deleted_objects.filter(pk=pk).exists())

    def assertEqualsFixture(self, data, path_to_response_fixture, export=False):
        path_to_fixture = self.responses_fixtures_dir + path_to_response_fixture
        if export:
            self.save_fixture(data, path_to_fixture)

        fixture = load_json(path_to_fixture)
        self.assertEquals(data, fixture)

    def assertNoContent(self, response):
        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)

    def assertOk(self, response):
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def assertCreated(self, response):
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

    def assertForbidden(self, response):
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

    def assertNotFound(self, response):
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)

    def assertBadRequest(self, response):
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def assertUnauthorized(self, response):
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def generate_fake_image(self):
        file = BytesIO()
        image = Image.new('RGBA', size=(100, 100), color=(155, 0, 0))
        image.save(file, 'png')
        file.name = 'fakeimage.png'
        file.seek(0)

        return file
