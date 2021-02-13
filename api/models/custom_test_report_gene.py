from django.db import models
from django.db.models import ForeignKey


class CustomTestReportGene(models.Model):
    class Meta:
        db_table = 'custom_test_report_gene'

    summary = models.TextField()

    custom_test_gene = ForeignKey('CustomTestGene', on_delete=models.CASCADE)
    custom_test_report = ForeignKey('CustomTestReport', on_delete=models.CASCADE)
