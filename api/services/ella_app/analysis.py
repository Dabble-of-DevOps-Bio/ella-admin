import json
import random

import pandas

from api.models import Analysis
from api.services.ella_app.api import EllaAppApiService


class AnalysisEllaAppService:

    def __init__(self):
        self.__api_service = EllaAppApiService()

    def generate_variant_report_data(self, auth_token, analysis_id, interpretation_id):
        self.__api_service.set_auth_token(auth_token)

        analysis_data = self.__get_parsed_analysis_data(analysis_id, interpretation_id)

        analysis_data = self.__set_filtered_transcripts_data(analysis_data)
        gene_data = self.__get_gene_data(analysis_data)

        random.shuffle(gene_data)

        df = pandas.DataFrame.from_records(gene_data)
        df = df.drop_duplicates()
        df = df.sort_values(by=['Variant Classification Code'], key=lambda x: x.map(Analysis.ACMG_CODES))
        df = df.drop_duplicates(subset=['Variant'])
        df = df.drop(columns=['Variant Classification Code'])

        variant_report_data = []
        for index, row in df.iterrows():
            variant_report_data.append({
                'gene': row['Gene'],
                'variant': row['Variant'],
                'zygosity': row['Zygosity'],
                'variant_classification': row['Variant Classification'],
            })

        variant_report_data.sort(key=lambda data: data['variant'])

        return variant_report_data

    def __get_parsed_analysis_data(self, analysis_id, interpretation_id):
        analysis_metadata = self.__get_analysis_metadata(analysis_id)

        filter_configs = self.__get_filter_configs(analysis_id)
        filter_config_id = self.__get_active_filter_config(filter_configs)

        allele_ids = self.__get_allele_ids(analysis_id, interpretation_id, filter_config_id)
        allele_assessments = self.__get_allele_assessments(analysis_id, interpretation_id,
                                                           filter_config_id, allele_ids)

        return {
            'allele_assessments': allele_assessments,
            'analysis_metadata': analysis_metadata,
            'filterconfigs': filter_configs,
        }

    def __set_filtered_transcripts_data(self, analysis_data):
        filtered_transcripts_report_data = []
        for allele_assessment in analysis_data['allele_assessments']:
            transcripts = allele_assessment['annotation']['transcripts']

            filtered_transcripts_ids = allele_assessment['annotation']['filtered_transcripts']
            filtered_transcripts_data = list(filter(lambda n: n['transcript'] in filtered_transcripts_ids, transcripts))
            for n in filtered_transcripts_data:
                filtered_transcripts_report_data.append(n)
            allele_assessment['filtered_transcripts'] = filtered_transcripts_report_data

        return analysis_data

    def __get_gene_data(self, analysis_data):
        gene_data = []
        for allele_assessment in analysis_data['allele_assessments']:
            transcripts = allele_assessment['filtered_transcripts']
            for transcript in transcripts:
                d = {
                    'Gene': transcript['symbol'],
                    'Variant': transcript['HGVSc'],
                    'Zygosity': allele_assessment['samples'][0]['genotype']['type'],
                    'Variant Classification': Analysis.ACMG_CODES[
                        str(allele_assessment['allele_assessment']['classification'])],
                    'Variant Classification Code': allele_assessment['allele_assessment']['classification']
                }
                gene_data.append(d)

        return gene_data

    def __get_analysis_metadata(self, analysis_id):
        response = self.__api_service.get('/api/v1/analyses/%s' % analysis_id)

        return json.loads(response.content.decode('utf-8'))

    def __get_filter_configs(self, analysis_id):
        response = self.__api_service.get('/api/v1/workflows/analyses/%s/filterconfigs/' % analysis_id)

        return json.loads(response.content.decode('utf-8'))

    def __get_allele_ids(self, analysis_id, interpretation_id, filter_config_id):
        payload = {'filterconfig': filter_config_id}

        response = self.__api_service.get(
            '/api/v1/workflows/analyses/%s/interpretations/%s/filteredalleles/' % (analysis_id, interpretation_id),
            payload)

        return json.loads(response.content.decode('utf-8'))['allele_ids']

    def __get_allele_assessments(self, analysis_id, interpretation_id, filter_config_id, allele_ids):
        payload = {
            'allele_ids': ','.join([str(x) for x in allele_ids]),
            'current': True,
            'filterconfig_id': filter_config_id
        }
        response = self.__api_service.get(
            '/api/v1/workflows/analyses/%s/interpretations/%s/alleles/' % (analysis_id, interpretation_id), payload)

        return json.loads(response.content.decode('utf-8'))

    def __get_active_filter_config(self, filter_configs):
        filter_config_id = None
        for filter_config in filter_configs:
            if filter_config['active']:
                filter_config_id = filter_config['id']
                break

        return filter_config_id
