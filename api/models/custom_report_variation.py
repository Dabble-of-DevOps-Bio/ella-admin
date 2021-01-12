from django.db import models
from django.db.models import ForeignKey


class CustomReportVariation(models.Model):
    class Meta:
        db_table = 'custom_report_variation'

    variation = models.CharField(max_length=255)
    custom_report_gene = ForeignKey('CustomReportGene', on_delete=models.CASCADE)
