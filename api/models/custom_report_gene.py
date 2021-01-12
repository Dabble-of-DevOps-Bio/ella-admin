from django.db import models
from django.db.models import ForeignKey


class CustomReportGene(models.Model):
    class Meta:
        db_table = 'custom_report_gene'

    name = models.CharField(max_length=255)

    custom_report_test = ForeignKey('CustomReportTest', on_delete=models.CASCADE)
