from django.conf.urls import url
from django.urls import include, path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from api.http.views import LogoutView, UserViewSet, AnalysisViewSet, VariantReportViewSet, GenePanelViewSet, \
    UserGroupViewSet, ProfileViewSet, StaffAppLoginView, CustomTestViewSet, CustomTestGeneViewSet, CustomTestReportViewSet, PatientViewSet

router = routers.DefaultRouter()

router.register(r'user-groups', UserGroupViewSet, basename='user_groups')
router.register(r'users', UserViewSet, basename='users')
router.register(r'analysis', AnalysisViewSet, basename='analysis')
router.register(r'gene-panels', GenePanelViewSet, basename='gene_panels')
router.register(r'custom-test-reports', CustomTestReportViewSet, basename='custom_test_reports')
router.register(r'custom-tests', CustomTestViewSet, basename='custom_tests')
router.register(r'custom-test-genes', CustomTestGeneViewSet, basename='custom_test_genes')
router.register(r'patients', PatientViewSet, basename='patients')
router.register(r'', ProfileViewSet, basename='profile')

urlpatterns = [
    path('logout/', LogoutView.as_view(), name='api_logout'),
    path('staff-app-login/', StaffAppLoginView.as_view(), name='staff_app_login'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('users/<int:user_pk>/move-to-inactive/',
         UserViewSet.as_view({'post': 'move_to_inactive_group',}), name='move_user_to_inactive_group'),

    path('analysis/<int:analysis_pk>/variant-report/',
         VariantReportViewSet.as_view({'get': 'retrieve', 'put': 'update'}), name='analysis_variant_report'),
    path('analysis/<int:analysis_pk>/patient-data/', AnalysisViewSet.as_view({'get': 'get_patient_data'}),
         name='analysis_patient_data'),

    path('custom-test-reports/<int:custom_test_report_pk>/pdf/', CustomTestReportViewSet.as_view({'get': 'generate_pdf'}), name='custom_test_reports_generate_pdf'),

    url(r'^', include(router.urls)),
    path('password-reset/', include('django_rest_passwordreset.urls', namespace='user')),
]
