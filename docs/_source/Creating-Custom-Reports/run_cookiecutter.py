#!/usr/bin/env python

from cookiecutter.main import cookiecutter
import os
import json

this_dir_path = os.path.dirname(os.path.realpath('__file__'))
#this_dir_path

TEMPLATE = os.path.join(this_dir_path, "cookiecutter")
ANALYSIS_DATA_FILE = '/docs/_source/reporting-data/analysis_data.json'

with open('cookiecutter.json', 'r') as reader:
    data = json.load(reader)

cookiecutter(
    TEMPLATE,  # path/url to cookiecutter template
    extra_context=data,
    output_dir='docs',
    no_input=True
)
