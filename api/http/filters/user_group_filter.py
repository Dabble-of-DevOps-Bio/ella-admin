from django_filters import rest_framework

from api.models import UserGroup


class UserGroupFilter(rest_framework.FilterSet):
    sort = rest_framework.OrderingFilter(
        fields=(
            ('name', 'name'),
        )
    )

    class Meta:
        model = UserGroup
        fields = ('name',)
