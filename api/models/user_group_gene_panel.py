from django.db import models

from api.models.base_model import BaseModel
from compositefk.fields import CompositeForeignKey


class UserGroupGenePanel(BaseModel):
    class Meta:
        db_table = 'usergroupgenepanel'

    group = models.ForeignKey('UserGroup', db_column='usergroup_id', on_delete=models.CASCADE)

    gene_panel_name = models.CharField(max_length=255, db_column='genepanel_name', blank=False)
    gene_panel_version = models.CharField(max_length=255, db_column='genepanel_version', blank=False)

    gene_panel = CompositeForeignKey('GenePanel', on_delete=models.CASCADE, to_fields={
        "name": "gene_panel_name",
        "version": "gene_panel_version"
    })
