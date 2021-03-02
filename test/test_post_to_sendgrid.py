import os

from django.core.mail import EmailMessage
from django.test import override_settings
from django.test.testcases import SimpleTestCase
from nose.plugins.skip import SkipTest


class TestPostToSendgrid(SimpleTestCase):
    def test_post(self):
        """
        Sends a POST to sendgrid's live API using a private API key that is stored
        in github.
        """

        SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
        if not SENDGRID_API_KEY:
            raise SkipTest("SENDGRID_API_KEY not set")

        # Set DEBUG=True so sandbox mode is enabled
        settings = {
            "DEBUG": True,
            "SENDGRID_API_KEY": SENDGRID_API_KEY,
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
