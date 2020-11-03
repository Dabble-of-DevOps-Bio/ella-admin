from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError
from rest_framework.validators import qs_exists, qs_filter


class UniqueFieldExternalValidator:
    """
    Add unique validation for serializer field.
    It helps us exclude existing entity on update.
    """
    message = _('This field must be unique.')

    def __init__(self, queryset, field_name, lookup='exact', message=None):
        self.queryset = queryset
        self.field_name = field_name
        self.message = message or self.message
        self.lookup = lookup

    def filter_queryset(self, queryset):
        """
        Filter the queryset to all instances matching the given attribute.
        """
        filter_kwargs = {'%s__%s' % (self.field_name, self.lookup): self.data[self.field_name]}
        return qs_filter(queryset, **filter_kwargs)

    def exclude_current_instance(self, queryset):
        """
        If an instance is being updated, then do not include
        that instance itself as a uniqueness conflict.
        """
        return queryset.exclude(pk=self.data['id'])

    def __call__(self, data, serializer):
        self.data = data

        queryset = self.queryset
        queryset = self.filter_queryset(queryset)

        if 'id' in data:
            queryset = self.exclude_current_instance(queryset)

        if qs_exists(queryset):
            raise ValidationError({self.field_name: self.message}, code='unique')
