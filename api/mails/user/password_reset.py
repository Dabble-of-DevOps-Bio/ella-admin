from django.conf import settings
from django.utils.translation import gettext as _

from api.mails import Mail


class PasswordReset(Mail):
    template_name = 'emails/user/password_reset.html'
    subject = _('Reset your Ella password')
    from_email = settings.EMAIL_SUPPORT_EMAIL
