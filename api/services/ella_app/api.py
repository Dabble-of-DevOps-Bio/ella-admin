import requests
from api.mocks import get_adapter_with_mocked_urls
from django.conf import settings


class EllaAppApiService:

    def __init__(self):
        self.__base_url = settings.ELLA_APP_URL

        self.__session = self.__get_session()
        self.__cookies = None

    def get(self, endpoint, payload=None):
        if payload is None:
            payload = {}

        url = self.__make_url(endpoint)

        return self.__session.get(url, params=payload, cookies=self.__cookies)

    def set_auth_token(self, token):
        self.__cookies = {'AuthenticationToken': token}

    def __make_url(self, endpoint):
        return self.__base_url + endpoint

    def __get_session(self):
        session = requests.Session()

        if settings.ENV == 'testing':
            self.__set_mocks(session)

        return session

    def __set_mocks(self, session):
        adapter = get_adapter_with_mocked_urls()

        session.mount('mock://', adapter)
