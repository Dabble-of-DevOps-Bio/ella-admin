import json

import pendulum
from rest_framework import mixins
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.http.serializers import StaffAppLoginSerializer, VariantReportSerializer
from api.http.views.view import BaseViewSet
from api.models import AnalysisInterpretation, VariantReport
from api.permissions import IsSuperuser
from api.services.ella_app import AnalysisEllaAppService


class VariantReportViewSet(BaseViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin):
    _request_permissions = {
        'retrieve': (IsAuthenticated, IsSuperuser),
        'update': (IsAuthenticated, IsSuperuser),
    }

    serializer_class = VariantReportSerializer
    queryset = VariantReport.objects.all()

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        analysis_id = kwargs.get('analysis_pk')
        interpretation_id = AnalysisInterpretation.objects.filter(analysis_id=analysis_id, finalized=True).order_by(
            '-date_last_update').first().pk

        variant_report = VariantReport.objects.filter(analysis_id=analysis_id,
                                                      analysis_interpretation_id=interpretation_id,
                                                      user_id=user.pk).first()

        if variant_report is None:
            variant_report_data = self.__generate_variant_report_data(user, analysis_id, interpretation_id)
            variant_report_data_json = json.dumps(variant_report_data)
            variant_report = VariantReport(data=variant_report_data_json, user_id=user.pk, analysis_id=analysis_id,
                                           analysis_interpretation_id=interpretation_id)
            variant_report.save()

        serializer = self.get_serializer(variant_report)

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        user = request.user
        analysis_id = kwargs.get('analysis_pk')
        interpretation_id = AnalysisInterpretation.objects.filter(analysis_id=analysis_id, finalized=True).order_by(
            '-date_last_update').first().pk

        variant_report = get_object_or_404(queryset=VariantReport.objects.all(), user_id=user.pk,
                                           analysis_interpretation_id=interpretation_id, analysis_id=analysis_id)


        serializer = self.get_serializer(variant_report, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def __generate_variant_report_data(self, user, analysis_id, interpretation_id):
        staff_app_login_serializer = StaffAppLoginSerializer()
        user_session, token = staff_app_login_serializer.create_staff_app_user_session(user)

        ella_app_service = AnalysisEllaAppService()
        variant_report_data = ella_app_service.generate_variant_report_data(auth_token=token, analysis_id=analysis_id,
                                                                            interpretation_id=interpretation_id)

        user_session.expires = pendulum.now().subtract(years=1)
        user_session.save()

        return variant_report_data
