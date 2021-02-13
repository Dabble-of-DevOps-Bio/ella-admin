import re

from django.conf import settings
from requests_mock import Adapter

from api.utilities.tests_helpers import load_json


def get_adapter_with_mocked_urls():
    adapter = Adapter()
    register_uri_list(adapter)

    return adapter


def register_uri_list(adapter: Adapter):
    register_get_analysis_allele_assessments_uri(adapter)
    register_get_analysis_filter_configs_uri(adapter)
    register_get_analysis_filtered_alleles_uri(adapter)
    register_get_analysis_metadata_uri(adapter)


def register_get_analysis_allele_assessments_uri(adapter: Adapter):
    matcher = re.compile(
        '%s/api/v1/workflows/analyses/%s/interpretations/%s/alleles/' % (settings.ELLA_APP_URL, '[0-9]+', '[0-9]+'))
    adapter.register_uri('GET', matcher, json=get_analysis_allele_assessments_data())


def register_get_analysis_filter_configs_uri(adapter: Adapter):
    matcher = re.compile('%s/api/v1/workflows/analyses/%s/filterconfigs/' % (settings.ELLA_APP_URL, '[0-9]+'))
    adapter.register_uri('GET', matcher, json=get_analysis_filter_configs_data())


def register_get_analysis_filtered_alleles_uri(adapter: Adapter):
    matcher = re.compile('%s/api/v1/workflows/analyses/%s/interpretations/%s/filteredalleles/' % (
        settings.ELLA_APP_URL, '[0-9]+', '[0-9]+'))
    adapter.register_uri('GET', matcher, json=get_analysis_filtered_alleles_data())


def register_get_analysis_metadata_uri(adapter: Adapter):
    matcher = re.compile('%s/api/v1/analyses/%s' % (settings.ELLA_APP_URL, '[0-9]+'))
    adapter.register_uri('GET', matcher, json=get_analysis_metadata_data())


def get_analysis_allele_assessments_data():
    return load_json('api/mocks/fixtures/ella_app_api_service/analysis_allele_assessments.json')


def get_analysis_filter_configs_data():
    return load_json('api/mocks/fixtures/ella_app_api_service/analysis_filter_configs.json')


def get_analysis_filtered_alleles_data():
    return load_json('api/mocks/fixtures/ella_app_api_service/analysis_filtered_alleles.json')


def get_analysis_metadata_data():
    return load_json('api/mocks/fixtures/ella_app_api_service/analysis_metadata.json')
