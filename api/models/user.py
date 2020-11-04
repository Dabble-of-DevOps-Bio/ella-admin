from enum import Enum

from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models import IntegerField, CharField, EmailField, DateTimeField, ForeignKey
from safedelete import SOFT_DELETE_CASCADE

from api.models.abstract_user import AbstractUser
from api.models.base_model import BaseModel
from api.models.managers import UserManager


class User(AbstractUser, BaseModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    class Group(Enum):
        ADMIN = 1
        STAFF = 2

    class Meta:
        db_table = 'user'

    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'username'

    objects = UserManager()

    first_name = CharField(max_length=255, null=False)
    last_name = CharField(max_length=255, null=False)
    username = CharField(max_length=255, null=False, unique=True)
    email = EmailField(blank=True)
    password_expiry = DateTimeField(null=True)
    incorrect_logins = IntegerField(default=0)
    config = JSONField(default=dict)

    group = ForeignKey('UserGroup', null=True, on_delete=models.CASCADE)

    @property
    def auth_group(self):
        return self.auth_groups.first()

    @property
    def is_active(self):
        return self.active
