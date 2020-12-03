from django.db.models import CharField, DateTimeField, ForeignKey, CASCADE

from api.models.base_model import BaseModel


class UserSession(BaseModel):
    class Meta:
        db_table = 'usersession'

    user = ForeignKey('User', on_delete=CASCADE)
    token = CharField(max_length=255, null=False, unique=True)

    issued = DateTimeField(auto_now=True, null=False)
    lastactivity = DateTimeField(auto_now=True, null=False)
    expires = DateTimeField(null=False)
    logged_out = DateTimeField(null=False)
