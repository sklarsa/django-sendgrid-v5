import os

from django.core.mail import EmailMessage
from django.test import override_settings
from django.test.testcases import SimpleTestCase


class TestPostToSendgrid(SimpleTestCase):

    def test_post(self):
        # Set DEBUG=True so sandbox mode is enabled
        settings = {
            "DEBUG": True,
            "SENDGRID_API_KEY": os.environ["SENDGRID_API_KEY"],
            "EMAIL_BACKEND": "sendgrid_backend.SendgridBackend",
        }

        with override_settings(**settings):
            msg = EmailMessage(
                subject="Hello, World!",
                body="Hello, World!",
                from_email="Sam Smith <sam.smith@example.com>",
                to=["John Doe <john.doe@example.com>"],
            )
            val = msg.send()
            self.assertEquals(val, 1)
