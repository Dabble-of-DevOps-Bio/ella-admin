from rest_framework import pagination
from rest_framework.response import Response

from api.http.pagination.paginator import Paginator


class PageNumberPagination(pagination.PageNumberPagination):
    page_query_param = 'page'
    page_size_query_param = 'per_page'
    page_size = 10
    django_paginator_class = Paginator

    def last_page_number(self):
        if self.page.paginator.get_all:
            return 1

        page_size = self.get_page_size(self.request)
        total_items = self.page.paginator.count
        last_page_number = total_items // page_size + bool(total_items % page_size)

        return last_page_number if last_page_number > 0 else 1

    def get_paginated_response(self, data):
        return Response({
            'total_items': self.page.paginator.count,
            'previous_page': self.page.previous_page_number() if self.page.has_previous() else None,
            'next_page': self.page.next_page_number() if self.page.has_next() else None,
            'last_page': self.last_page_number(),
            'items': data
        })

    def paginate_queryset(self, queryset, request, view=None):
        page_size = self.get_page_size(request)
        paginator = self.django_paginator_class(queryset, page_size)

        if request.query_params.get('all', False):
            self.request = request
            self.page = paginator.all()

            return list(self.page)

        return super().paginate_queryset(queryset, request, view)
