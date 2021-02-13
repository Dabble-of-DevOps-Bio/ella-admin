from django.db import models

from api.models.base_model import BaseModel


class GenePanel(BaseModel):
    class Meta:
        db_table = 'genepanel'
        constraints = [
            models.UniqueConstraint(fields=['name', 'version'], name='name_version_unique')
        ]

    name = models.CharField(max_length=255, blank=False)
    version = models.CharField(max_length=255, blank=False)
    genome_reference = models.CharField(max_length=255, blank=False)
    official = models.BooleanField(null=False)
    date_created = models.DateTimeField(blank=False)

    user = models.ForeignKey('User', null=True, on_delete=models.CASCADE)

    groups = models.ManyToManyField(
        'UserGroup',
        through='UserGroupGenePanel',
        through_fields=('gene_panel', 'group',)
    )
