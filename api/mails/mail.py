import os

from django.core.mail import EmailMessage
from django.template.loader import get_template


class Mail:
    to = []
    from_email = ''
    subject = ''
    template_name = ''
    context = {}

    def set_to(self, to):
        if type(to) is list:
            self.to = to
        else:
            self.to = [to]

        return self

    def set_subject(self, subject):
        self.subject = subject
        return self

    def set_from_email(self, from_email):
        self.from_email = from_email
        return self

    def set_context(self, context):
        if self.context:
            self.context.update(context)
        else:
            self.context = context

        return self

    def send(self):
        body = get_template(self.template_name).render(self.context)

        message = EmailMessage(self.subject, body, to=self.to, from_email=self.from_email)
        message.content_subtype = 'html'

        return message.send()
