import pendulum

from django.core.files.base import ContentFile
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from wkhtmltopdf.views import PDFTemplateResponse

from api.http.filters import CustomTestReportFilter
from api.http.serializers.custom_test_report_serializer import CustomTestReportSerializer
from api.http.views.view import BaseViewSet
from api.models import CustomTestReport
from api.permissions import IsSuperuser


class CustomTestReportViewSet(BaseViewSet, ModelViewSet):
    _request_permissions = {
        'update': (IsAuthenticated, IsSuperuser,),
        'partial_update': (IsAuthenticated, IsSuperuser,),
        'create': (IsAuthenticated, IsSuperuser),
        'retrieve': (IsAuthenticated, IsSuperuser),
        'list': (IsAuthenticated, IsSuperuser),
        'destroy': (IsAuthenticated, IsSuperuser),
        'generate_pdf': (IsAuthenticated, IsSuperuser)
    }

    serializer_class = CustomTestReportSerializer
    queryset = CustomTestReport.objects.all()
    filterset_class = CustomTestReportFilter
    search_fields = []

    @action(detail=False, methods=['GET'])
    def generate_pdf(self, request, *args, **kwargs):
        custom_test_report_pk = self.kwargs['custom_test_report_pk']
        custom_test_report = CustomTestReport.objects.get(pk=custom_test_report_pk)

        file_name = self.__get_pdf_report_file_name(custom_test_report)

        custom_test_report_serializer = CustomTestReportSerializer(custom_test_report, expand=[
            'custom_test.custom_test_genes',
            'custom_test_report_genes.custom_test_gene', 'custom_test_report_variations.custom_test_variation'
        ])

        pdf_response = PDFTemplateResponse(
            request=request,
            template='pdf/custom_test_report.html',
            context={
                'custom_test_report': custom_test_report_serializer.data,
            },
            filename=('%s.pdf' % file_name),
            show_content_in_browser=False
        )

        pdf_file = ContentFile(pdf_response.rendered_content)
        pdf_file.name = 'file.pdf'

        return pdf_response

    def __get_pdf_report_file_name(self, custom_test_report: CustomTestReport):
        custom_test_name = custom_test_report.custom_test.name
        current_date = pendulum.now().to_datetime_string().replace(' ', '_')

        return '%s-%s' % (custom_test_name, current_date)
