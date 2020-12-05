from compositefk.fields import CompositeForeignKey
from django.contrib.postgres.fields import JSONField
from django.db import models


class Analysis(models.Model):
    class Meta:
        db_table = 'analysis'

    name = models.CharField(max_length=255, unique=True, blank=False)

    gene_panel_name = models.CharField(max_length=255, db_column='genepanel_name', blank=False)
    gene_panel_version = models.CharField(max_length=255, db_column='genepanel_version', blank=False)

    gene_panel = CompositeForeignKey('GenePanel', on_delete=models.CASCADE, to_fields={
        "name": "gene_panel_name",
        "version": "gene_panel_version"
    })

    warnings = models.CharField(max_length=255)
    report = models.CharField(max_length=255)
    date_deposited = models.DateTimeField(blank=False)
    properties = JSONField()
    date_requested = models.DateTimeField()
