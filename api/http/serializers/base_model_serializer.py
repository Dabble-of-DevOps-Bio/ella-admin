from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework.exceptions import ValidationError
from rest_framework.fields import ReadOnlyField, DateTimeField


class BaseModelSerializer(FlexFieldsModelSerializer):
    id = ReadOnlyField()
    created_at = DateTimeField(read_only=True)
    updated_at = DateTimeField(read_only=True)

    def non_field_fail(self, name: str, error_key: str = None):
        error_key = name if error_key is None else error_key
        message = self.default_error_messages[error_key]

        raise ValidationError({name: message})

    def _divide_data(self, data):
        existing_entities_data = list()
        new_entities_data = list()

        for elem in data:
            if 'id' in elem and elem['id'] is not None:
                existing_entities_data.append(elem)
            else:
                new_entities_data.append(elem)

        return new_entities_data, existing_entities_data
