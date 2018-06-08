from future.builtins import str
import base64
from email.mime.base import MIMEBase
import email.utils
import mimetypes
import sys
import uuid
import warnings

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMultiAlternatives
from django.core.mail.backends.base import BaseEmailBackend

import sendgrid
from sendgrid.helpers.mail import (
    ASM, Attachment, Category, Content, Email, Header, Mail, MailSettings, OpenTracking,
    Personalization, SandBoxMode, Substitution, TrackingSettings
)

from python_http_client.exceptions import HTTPError

if sys.version_info >= (3.0, 0.0):
    basestring = str


class SendgridBackend(BaseEmailBackend):
    """
    Inherits from and implements the required methods of django.core.mail.backends.base.BaseEmailBackend
    using the sendgrid python api (v5.0+)

    This class uses the api key set in the django setting, SENDGRID_API_KEY.  If you have not set this value (or wish
    to override it), this backend accepts an api_key argument that supersedes the django setting
    """
    def __init__(self, *args, **kwargs):
        super(SendgridBackend, self).__init__(*args, **kwargs)

        if "api_key" in kwargs:
            self.sg = sendgrid.SendGridAPIClient(api_key=kwargs["api_key"])
        elif hasattr(settings, "SENDGRID_API_KEY") and settings.SENDGRID_API_KEY:
            self.sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        else:
            raise ImproperlyConfigured("settings.py must contain a value for SENDGRID_API_KEY.  " +
                                       "You may also pass a value to the api_key argument (optional).")

        sandbox_mode_in_debug = True
        if hasattr(settings, "SENDGRID_SANDBOX_MODE_IN_DEBUG"):
            sandbox_mode_in_debug = settings.SENDGRID_SANDBOX_MODE_IN_DEBUG

        self.sandbox_mode = settings.DEBUG and sandbox_mode_in_debug

        if self.sandbox_mode:
            warnings.warn("Sendgrid email backend is in sandbox mode!  Emails will not be delivered.")

        track_email = True
        if hasattr(settings, "SENDGRID_TRACK_EMAIL_OPENS"):
            track_email = settings.SENDGRID_TRACK_EMAIL_OPENS

        self.track_email = track_email

    def send_messages(self, email_messages):
        success = 0
        for msg in email_messages:
            data = self._build_sg_mail(msg)

            try:
                resp = self.sg.client.mail.send.post(request_body=data)
                msg.extra_headers['status'] = resp.status_code
                x_message_id = resp.headers.get('x-message-id', None)
                if x_message_id:
                    msg.extra_headers['message_id'] = x_message_id
                success += 1
            except HTTPError:
                if not self.fail_silently:
                    raise
        return success

    def _parse_email_address(self, address):
        name, addr = email.utils.parseaddr(address)
        if not name:
            name = None
        return addr, name

    def _build_sg_mail(self, msg):
        mail = Mail()

        mail.from_email = Email(*self._parse_email_address(msg.from_email))
        mail.subject = msg.subject

        personalization = Personalization()
        for addr in msg.to:
            personalization.add_to(Email(*self._parse_email_address(addr)))

        for addr in msg.cc:
            personalization.add_cc(Email(*self._parse_email_address(addr)))

        for addr in msg.bcc:
            personalization.add_bcc(Email(*self._parse_email_address(addr)))

        personalization.subject = msg.subject

        for k, v in msg.extra_headers.items():
            if k.lower() == "reply-to":
                mail.reply_to = Email(v)
            else:
                personalization.add_header(Header(k, v))

        if hasattr(msg, "template_id"):
            mail.template_id = msg.template_id
            if hasattr(msg, "substitutions"):
                for k, v in msg.substitutions.items():
                    personalization.add_substitution(Substitution(k, v))

        # write through the ip_pool_name attribute
        if hasattr(msg, "ip_pool_name"):
            if not isinstance(msg.ip_pool_name, basestring):
                raise ValueError(
                    "ip_pool_name must be a string, got: {}; "
                    "see https://sendgrid.com/docs/API_Reference/Web_API_v3/Mail/index.html#-Request-Body-Parameters".format(
                        type(msg.ip_pool_name)))
            if not 2 <= len(msg.ip_pool_name) <= 64:
                raise ValueError(
                    "the number of characters of ip_pool_name must be min 2 and max 64, got: {}; "
                    "see https://sendgrid.com/docs/API_Reference/Web_API_v3/Mail/index.html#-Request-Body-Parameters".format(
                        len(msg.ip_pool_name)))
            mail.ip_pool_name = msg.ip_pool_name

        # write through the send_at attribute
        if hasattr(msg, "send_at"):
            if not isinstance(msg.send_at, int):
                raise ValueError(
                    "send_at must be an integer, got: {}; "
                    "see https://sendgrid.com/docs/API_Reference/SMTP_API/scheduling_parameters.html#-Send-At".format(
                        type(msg.send_at)))
            personalization.send_at = msg.send_at

        mail.add_personalization(personalization)

        if hasattr(msg, "reply_to") and msg.reply_to:
            if mail.reply_to:
                # If this code path is triggered, the reply_to on the sg mail was set in a header above
                reply_to = Email(*self._parse_email_address(msg.reply_to))
                if reply_to.email != mail.reply_to.email or reply_to.name != mail.reply_to.name:
                    raise ValueError("Sendgrid only allows 1 email in the reply-to field.  " +
                                     "Reply-To header value != reply_to property value.")

            if not isinstance(msg.reply_to, basestring):
                if len(msg.reply_to) > 1:
                    raise ValueError("Sendgrid only allows 1 email in the reply-to field")
                mail.reply_to = Email(*self._parse_email_address(msg.reply_to[0]))
            else:
                mail.reply_to = Email(*self._parse_email_address(msg.reply_to))

        for attch in msg.attachments:
            attachment = Attachment()

            if isinstance(attch, MIMEBase):
                filename = attch.get_filename()
                if not filename:
                    ext = mimetypes.guess_extension(attch.get_content_type())
                    filename = "part-{0}{1}".format(uuid.uuid4().hex, ext)
                attachment.filename = filename
                # todo: Read content if stream?
                attachment.content = attch.get_payload().replace("\n", "")
                attachment.type = attch.get_content_type()
                content_id = attch.get("Content-ID")
                if content_id:
                    # Strip brackets since sendgrid's api adds them
                    if content_id.startswith("<") and content_id.endswith(">"):
                        content_id = content_id[1:-1]
                    attachment.content_id = content_id
                    attachment.disposition = "inline"

            else:
                filename, content, mimetype = attch

                attachment.filename = filename
                # todo: Read content if stream?
                if isinstance(content, str):
                    content = content.encode()
                attachment.content = base64.b64encode(content).decode()
                attachment.type = mimetype

            mail.add_attachment(attachment)

        msg.body = ' ' if msg.body == '' else msg.body

        if isinstance(msg, EmailMultiAlternatives):
            mail.add_content(Content("text/plain", msg.body))
            for alt in msg.alternatives:
                if alt[1] == "text/html":
                    mail.add_content(Content(alt[1], alt[0]))
        elif msg.content_subtype == "html":
            mail.add_content(Content("text/plain", " "))
            mail.add_content(Content("text/html", msg.body))
        else:
            mail.add_content(Content("text/plain", msg.body))

        if hasattr(msg, "categories"):
            for cat in msg.categories:
                mail.add_category(Category(cat))

        if hasattr(msg, "asm"):
            if "group_id" not in msg.asm:
                raise KeyError("group_id not found in asm")

            if "groups_to_display" in msg.asm:
                mail.asm = ASM(msg.asm["group_id"], msg.asm["groups_to_display"])
            else:
                mail.asm = ASM(msg.asm["group_id"])

        mail_settings = MailSettings()
        mail_settings.sandbox_mode = SandBoxMode(self.sandbox_mode)
        mail.mail_settings = mail_settings

        tracking_settings = TrackingSettings()
        tracking_settings.open_tracking = OpenTracking(self.track_email)
        mail.tracking_settings = tracking_settings

        return mail.get()
