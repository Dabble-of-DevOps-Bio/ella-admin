from django.contrib.postgres.fields import JSONField

from api.models.base_model import BaseModel
from django.db import models


class VariantReport(BaseModel):
    class Meta:
        db_table = 'variantreport'

    analysis = models.ForeignKey('Analysis', on_delete=models.CASCADE)
    analysis_interpretation = models.ForeignKey('AnalysisInterpretation', on_delete=models.CASCADE)
    user = models.ForeignKey('User', on_delete=models.CASCADE)

    data = JSONField(default=dict)

    comment = models.CharField(max_length=255, blank=True)
    literature = models.CharField(max_length=255, blank=True)
