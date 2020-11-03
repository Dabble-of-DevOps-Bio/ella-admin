from django.db.models import DateTimeField
from safedelete.models import SafeDeleteModel


class BaseModel(SafeDeleteModel):
    class Meta:
        abstract = True

    created_at = DateTimeField(auto_now_add=True, null=False, editable=False, blank=False)
    updated_at = DateTimeField(auto_now=True, null=False, editable=False, blank=False)
