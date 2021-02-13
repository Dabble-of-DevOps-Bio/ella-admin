from django_filters import rest_framework

from api.models import User


class UserFilter(rest_framework.FilterSet):
    sort = rest_framework.OrderingFilter(
        fields=(
            ('last_name', 'last_name'),
            ('first_name', 'first_name'),
            ('username', 'username'),
            ('email', 'email'),
        )
    )

    class Meta:
        model = User
        fields = ('last_name', 'first_name', 'username', 'email',)
