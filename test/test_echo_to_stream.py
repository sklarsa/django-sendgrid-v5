import os
import sys
if sys.version_info >= (3.0, 0.0):
    from unittest.mock import MagicMock
else:
    from mock import MagicMock

from django.core.mail import EmailMessage
from django.test import override_settings
from django.test.testcases import SimpleTestCase

from sendgrid_backend.mail import SendgridBackend


class TestEchoToOutput(SimpleTestCase):
    def test_echo(self):
        settings = {
            "DEBUG": True,
            "SENDGRID_API_KEY": os.environ["SENDGRID_API_KEY"],
            "EMAIL_BACKEND": "sendgrid_backend.SendgridBackend",
            "SENDGRID_ECHO_TO_STDOUT": True
        }
        with override_settings(**settings):
            mocked_output_stream = MagicMock()
            connection = SendgridBackend(stream=mocked_output_stream)
            msg = EmailMessage(
                subject="Hello, World!",
                body="Hello, World!",
                from_email="Sam Smith <sam.smith@example.com>",
                to=["John Doe <john.doe@example.com>"],
                connection=connection,
            )
            msg.send()
            self.assertTrue(mocked_output_stream.write.called)
