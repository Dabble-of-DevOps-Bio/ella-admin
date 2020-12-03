from django.contrib.postgres.fields import JSONField
from django.db.models import CharField

from api.models.base_model import BaseModel


class UserGroup(BaseModel):
    class Meta:
        db_table = 'usergroup'

    name = CharField(max_length=255, null=False, unique=True)
    config = JSONField(default=dict)
