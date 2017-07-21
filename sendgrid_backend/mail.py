import base64
from email.mime.base import MIMEBase

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMultiAlternatives
from django.core.mail.backends.base import BaseEmailBackend

import sendgrid
from sendgrid.helpers.mail import (
    Attachment, Category, Content, Email, Header, Mail, Personalization, Substitution
)

try:
    from urllib.error import HTTPError
except ImportError:
    from urllib2 import HTTPError


class SendgridBackend(BaseEmailBackend):
    def __init__(self, *args, **kwargs):
        super(SendgridBackend, self).__init__(*args, **kwargs)

        if hasattr(settings, "SENDGRID_API_KEY"):
            self.sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        elif "api_key" in kwargs:
            self.sg = sendgrid.SendGridAPIClient(api_key=kwargs["api_key"])
        else:
            raise ImproperlyConfigured("settings.py must contain a value for SENDGRID_API_KEY")

    def send_messages(self, email_messages):
        success = 0
        for msg in email_messages:
            data = self._build_sg_mail(msg)
            try:
                self.sg.client.mail.send.post(request_body=data)
                success += 1
            except HTTPError as e:
                if not self.fail_silently:
                    raise
        return success

    def _build_sg_mail(self, msg):
        mail = Mail()

        mail.from_email = Email(msg.from_email)
        mail.subject = msg.subject

        personalization = Personalization()
        for addr in msg.to:
            personalization.add_to(Email(addr))

        for addr in msg.cc:
            personalization.add_cc(Email(addr))

        for addr in msg.bcc:
            personalization.add_bcc(Email(addr))

        personalization.subject = msg.subject

        for k, v in msg.extra_headers:
            personalization.add_header(Header(k, v))

        if hasattr(msg, "template_id"):
            mail.set_template_id(msg.template_id)
            if hasattr(msg, "substitutions"):
                for k, v in msg.substitutions.items():
                    personalization.add_substitution(Substitution(k, v))

        mail.add_personalization(personalization)

        for attch in msg.attachments:
            attachment = Attachment()

            if isinstance(attch, MIMEBase):
                attachment.filename = attch.get_filename()
                # todo: Read content if stream?
                attachment.content = base64.b64encode(attch.content)
                attachment.type = attch._subtype
                content_id = attch.get("Content-ID")
                if content_id:
                    attachment.content_id = content_id
                    attachment.disposition = "inline"

            else:
                filename, content, mimetype = attch

                attachment.filename = filename
                # todo: Read content if stream?
                attachment.content = content
                attachment.type = mimetype

            mail.add_attachment(attachment)

        if isinstance(msg, EmailMultiAlternatives):
            alts = False
            for alt in msg.alternatives:
                if alt[1] == "text/html":
                    alts = True
                    mail.add_content(Content(alt[1], alt[0]))

            if not alts:
                mail.add_content(Content("text/plain", msg.body))

        elif msg.content_subtype == "html":
            mail.add_content(Content("text/plain", " "))
            mail.add_content(Content("text/html", msg.body))
        else:
            mail.add_content(Content("text/plain", msg.body))

        if hasattr(msg, "categories"):
            for cat in msg.categories:
                mail.add_category(Category(cat))

        return mail.get()
