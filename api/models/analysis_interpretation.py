from compositefk.fields import CompositeForeignKey
from django.contrib.postgres.fields import JSONField
from django.db import models

from django.utils.translation import gettext_lazy as _


class AnalysisInterpretation(models.Model):
    class Meta:
        db_table = 'analysisinterpretation'

    class Status(models.TextChoices):
        NOT_STARTED = 'Not started', _('Not started')
        ONGOING = 'Ongoing', _('Ongoing')
        DONE = 'Done', _('Done')

    class WorkflowStatus(models.TextChoices):
        NOT_READY = 'Not ready', _('Not ready')
        INTERPRETATION = 'Interpretation', _('Interpretation')
        REVIEW = 'Review', _('Review')
        MEDICAL_REVIEW = 'Medical review', _('Medical review')

    analysis = models.ForeignKey('Analysis', on_delete=models.CASCADE, null=False)
    user = models.ForeignKey('User', on_delete=models.CASCADE, null=False)

    gene_panel_name = models.CharField(max_length=255, db_column='genepanel_name', blank=False)
    gene_panel_version = models.CharField(max_length=255, db_column='genepanel_version', blank=False)

    gene_panel = CompositeForeignKey('GenePanel', on_delete=models.CASCADE, to_fields={
        "name": "gene_panel_name",
        "version": "gene_panel_version"
    })

    user_state = JSONField()
    state = JSONField()

    status = models.CharField(max_length=255, choices=Status.choices)
    workflow_status = models.CharField(max_length=255, choices=WorkflowStatus.choices)

    date_last_update = models.DateTimeField()
    date_created = models.DateTimeField()

    finalized = models.BooleanField()
