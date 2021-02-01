from rest_framework import serializers
from rest_framework.exceptions import NotFound
from django.utils.translation import gettext_lazy as _


class UserAuthGroup(serializers.RelatedField):
    """
    Create custom serializer for user Group.
    By default user can have multiple roles, but in current system user should have only one role.
    This requirement force us to validate many-to-many field as many-to-one
    without overriding default DRF user model relations.
    """
    def to_internal_value(self, data):
        if not self.choices.__contains__(data):
            raise NotFound(detail=_('Auth Group not found'), code='auth_group')
        return data

    def to_representation(self, value):
        return value.pk
