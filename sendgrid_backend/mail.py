import base64
import email.utils
import io
import logging
import mimetypes
import sys
import threading
import uuid
import warnings
from email.mime.base import MIMEBase
from typing import TYPE_CHECKING, Dict, Iterable, Optional, Tuple, Union

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.core.mail.backends.base import BaseEmailBackend
from python_http_client.exceptions import HTTPError
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
    Attachment,
    Category,
    ClickTracking,
    Content,
    CustomArg,
    Email,
    Header,
    Mail,
    MailSettings,
    OpenTracking,
    Personalization,
    SandBoxMode,
    Substitution,
    TrackingSettings,
)

from sendgrid_backend.signals import sendgrid_email_sent
from sendgrid_backend.util import SENDGRID_5, SENDGRID_6, get_django_setting

DjangoAttachment = Union[Tuple[str, Union[bytes, str], str], MIMEBase]

# Need to change imports because of breaking changes in sendgrid's v6 api
# https://github.com/sendgrid/sendgrid-python/releases/tag/v6.0.0
if SENDGRID_5:
    from sendgrid.helpers.mail import ASM
else:
    from sendgrid.helpers.mail import Asm as ASM
    from sendgrid.helpers.mail import IpPoolName

logger = logging.getLogger(__name__)


class SendgridBackend(BaseEmailBackend):
    """
    Inherits from and implements the required methods of django.core.mail.backends.base.BaseEmailBackend
    using the sendgrid python api (v5.0+)

    This class uses the api key set in the django setting, SENDGRID_API_KEY.  If you have not set this value (or wish
    to override it), this backend accepts an api_key argument that supersedes the django setting
    """

    if TYPE_CHECKING:
        fail_silently = False

    def __init__(self, *args, **kwargs):
        super(SendgridBackend, self).__init__(*args, **kwargs)

        # Check for the API key either in the SENDGRID_API_KEY django setting,
        # or passed as an argument to the init function, which takes precedence
        # over the setting.

        if "api_key" in kwargs:
            self.sg = SendGridAPIClient(api_key=kwargs["api_key"])
        elif hasattr(settings, "SENDGRID_API_KEY") and settings.SENDGRID_API_KEY:
            self.sg = SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        else:
            raise ImproperlyConfigured(
                "settings.py must contain a value for SENDGRID_API_KEY.  "
                + "You may also pass a value to the api_key argument (optional)."
            )

        # Configure sandbox mode based on settings
        sandbox_mode_in_debug = get_django_setting(
            "SENDGRID_SANDBOX_MODE_IN_DEBUG", True
        )
        self.sandbox_mode = bool(settings.DEBUG) and bool(sandbox_mode_in_debug)

        if self.sandbox_mode:
            warnings.warn(
                "Sendgrid email backend is in sandbox mode!  Emails will not be delivered."
            )

        # Configure open & click tracking settings, which apply to all emails
        # sent from this backend.
        self.track_email = get_django_setting("SENDGRID_TRACK_EMAIL_OPENS", True)
        self.track_clicks_html = get_django_setting("SENDGRID_TRACK_CLICKS_HTML", True)
        self.track_clicks_plain = get_django_setting(
            "SENDGRID_TRACK_CLICKS_PLAIN", True
        )

        # Configure echoing sent email messages to stdout (or another stream)
        # for debugging purposes.
        self._lock = None  # type: Optional[threading._RLock]
        self.stream = None  # type: Optional[io.TextIOBase]

        if get_django_setting("SENDGRID_ECHO_TO_STDOUT"):
            self._lock = threading.RLock()
            self.stream = kwargs.pop("stream", sys.stdout)

    @staticmethod
    def _write_to_stream(stream: io.TextIOBase, message: EmailMessage) -> None:
        """
        Internal method used to serialize an email in plaintext to a stream
        """
        assert stream is not None

        msg = message.message()
        msg_data = msg.as_bytes()
        charset = (
            msg.get_charset().get_output_charset() if msg.get_charset() else "utf-8"
        )
        msg_data = msg_data.decode(charset)
        stream.write("%s\n" % msg_data)
        stream.write("-" * 79)
        stream.write("\n")

    def echo_to_output_stream(self, email_messages: Iterable[EmailMessage]) -> None:
        """
        Write all messages to the stream in a thread-safe way.
        """
        assert self._lock is not None
        assert self.stream is not None

        if not email_messages:
            return
        with self._lock:
            try:
                stream_created = self.open()
                for message in email_messages:
                    self._write_to_stream(self.stream, message)
                    self.stream.flush()  # flush after each message
                if stream_created:
                    self.close()
            except Exception:
                if not self.fail_silently:
                    raise

    def send_messages(self, email_messages: Iterable[EmailMessage]) -> int:
        """
        Sends a list of EmailMessage objects via Sendgrid's HTTP API.
        Returns an integer representing the number of messages sent.

        This implements django's BaseEmailBackend.send_messages method
        """
        if self.stream:
            self.echo_to_output_stream(email_messages)
        success = 0
        for msg in email_messages:
            data = self._build_sg_mail(msg)

            fail_flag = True
            try:
                resp = self.sg.client.mail.send.post(request_body=data)
                msg.extra_headers["status"] = resp.status_code
                x_message_id = resp.headers.get("x-message-id", None)
                if x_message_id:
                    msg.extra_headers["message_id"] = x_message_id
                else:
                    logger.warning("No x_message_id header received from sendgrid api")
                success += 1
                fail_flag = False
            except HTTPError as e:
                logger.error("Failed to send email %s" % e)
                if not self.fail_silently:
                    raise
            finally:
                sendgrid_email_sent.send(
                    sender=self.__class__, message=msg, fail_flag=fail_flag
                )
        return success

    def _create_sg_attachment(self, django_attch: DjangoAttachment) -> Attachment:
        """
        Handles the conversion between a django attachment object and a sendgrid attachment object.
        Due to differences between sendgrid's API versions, use this method when constructing attachments to ensure
        that attachments get properly instantiated.
        """

        def set_prop(attachment, prop_name, value):
            if SENDGRID_5:
                setattr(attachment, prop_name, value)
            else:
                if prop_name == "filename":
                    prop_name = "name"
                setattr(attachment, "file_{}".format(prop_name), value)

        sg_attch = Attachment()

        if isinstance(django_attch, MIMEBase):
            filename = django_attch.get_filename()
            if not filename:
                ext = mimetypes.guess_extension(django_attch.get_content_type())
                filename = "part-{0}{1}".format(uuid.uuid4().hex, ext)
            set_prop(sg_attch, "filename", filename)
            # todo: Read content if stream?
            set_prop(sg_attch, "content", django_attch.get_payload().replace("\n", ""))
            set_prop(sg_attch, "type", django_attch.get_content_type())
            content_id = django_attch.get("Content-ID")
            if content_id:
                # Strip brackets since sendgrid's api adds them
                if content_id.startswith("<") and content_id.endswith(">"):
                    content_id = content_id[1:-1]
                # These 2 properties did not change in v6, so we set them the usual way
                sg_attch.content_id = content_id
                sg_attch.disposition = "inline"

        else:
            filename, content, mimetype = django_attch

            set_prop(sg_attch, "filename", filename)

            # todo: Read content if stream?

            if isinstance(content, str):
                content = content.encode()

            set_prop(sg_attch, "content", base64.b64encode(content).decode())
            set_prop(sg_attch, "type", mimetype)

        return sg_attch

    def _parse_email_address(self, address: str) -> Tuple[str, Optional[str]]:
        """
        Returns a tuple of (addr, name) from an address string
        """
        name, addr = email.utils.parseaddr(address)  # type: Optional[str], str
        if not name:
            name = None
        return addr, name

    def _build_sg_mail(self, msg: EmailMessage) -> Dict:
        """
        Serializes a Django EmailMessage into its JSON representation.

        Returns a Dict of mail data to be consumed by the sendgrid api.
        """
        mail = Mail()

        mail.from_email = Email(*self._parse_email_address(msg.from_email))

        personalization = Personalization()
        for addr in msg.to:
            personalization.add_to(Email(*self._parse_email_address(addr)))

        for addr in msg.cc:
            personalization.add_cc(Email(*self._parse_email_address(addr)))

        for addr in msg.bcc:
            personalization.add_bcc(Email(*self._parse_email_address(addr)))

        if hasattr(msg, "custom_args"):
            for k, v in msg.custom_args.items():
                personalization.add_custom_arg(CustomArg(k, v))

        if self._is_transaction_template(msg):
            if msg.subject:
                logger.warning(
                    "Message subject is ignored in transactional template, "
                    "please add it as template variable (e.g. {{ subject }}"
                )
                # See https://github.com/sendgrid/sendgrid-nodejs/issues/843
        else:
            personalization.subject = msg.subject

        for k, v in msg.extra_headers.items():
            if k.lower() == "reply-to":
                mail.reply_to = Email(v)
            else:
                personalization.add_header(Header(k, v))

        if hasattr(msg, "ip_pool_name"):
            if not isinstance(msg.ip_pool_name, str):
                raise ValueError(
                    "ip_pool_name must be a str, got: {}; ".format(
                        type(msg.ip_pool_name)
                    )
                )

            # Validate ip_pool_name length before attempting to add
            if not 2 <= len(msg.ip_pool_name) <= 64:
                raise ValueError(
                    "the number of characters of ip_pool_name must be min 2 and max 64, got: {}; "
                    "see https://sendgrid.com/docs/API_Reference/Web_API_v3/Mail/"
                    "index.html#-Request-Body-Parameters".format(len(msg.ip_pool_name))
                )

            if SENDGRID_5:
                ip_pool_name = msg.ip_pool_name
            else:
                ip_pool_name = IpPoolName(msg.ip_pool_name)
            mail.ip_pool_name = ip_pool_name

        # write through the send_at attribute
        if hasattr(msg, "send_at"):
            if not isinstance(msg.send_at, int):
                raise ValueError(
                    "send_at must be an integer, got: {}; "
                    "see https://sendgrid.com/docs/API_Reference/SMTP_API/scheduling_parameters.html#-Send-At".format(
                        type(msg.send_at)
                    )
                )
            personalization.send_at = msg.send_at

        if hasattr(msg, "reply_to") and msg.reply_to:
            if mail.reply_to:
                # If this code path is triggered, the reply_to on the sg mail was set in a header above
                reply_to = Email(*self._parse_email_address(msg.reply_to[0]))
                if (
                    reply_to.email != mail.reply_to.email
                    or reply_to.name != mail.reply_to.name
                ):
                    raise ValueError(
                        "Sendgrid only allows 1 email in the reply-to field.  "
                        + "Reply-To header value != reply_to property value."
                    )

            if not isinstance(msg.reply_to, str):
                if len(msg.reply_to) > 1:
                    raise ValueError(
                        "Sendgrid only allows 1 email in the reply-to field"
                    )
                mail.reply_to = Email(*self._parse_email_address(msg.reply_to[0]))
            else:
                mail.reply_to = Email(*self._parse_email_address(msg.reply_to))

        for attch in msg.attachments:
            sg_attch = self._create_sg_attachment(attch)
            mail.add_attachment(sg_attch)

        if self._is_transaction_template(msg):
            if msg.body:
                logger.warning("Message body is ignored in transactional template")
        else:
            msg.body = " " if msg.body == "" else msg.body

        if hasattr(msg, "template_id"):
            # Template mails should not have subject and content attributes
            mail.template_id = msg.template_id
            if hasattr(msg, "substitutions"):
                for k, v in msg.substitutions.items():
                    personalization.add_substitution(Substitution(k, v))
            if hasattr(msg, "dynamic_template_data"):
                if SENDGRID_5:
                    logger.warning(
                        "dynamic_template_data not available in sendgrid version < 6"
                    )
                personalization.dynamic_template_data = msg.dynamic_template_data

        if not self._is_transaction_template(msg):
            # In sendgrid v6 we should not specify subject and content between request parameter
            # when we are sending a request for a transactional template
            mail.subject = msg.subject
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

        mail.add_personalization(personalization)

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
        tracking_settings.click_tracking = ClickTracking(
            self.track_clicks_html, self.track_clicks_plain
        )

        mail.tracking_settings = tracking_settings

        return mail.get()

    def _is_transaction_template(self, msg: EmailMessage) -> bool:
        return SENDGRID_6 and hasattr(msg, "template_id")
