import os

import pytest
from django.core.mail import EmailMessage
from django.test import override_settings
from django.test.testcases import SimpleTestCase


class TestPostToSendgrid(SimpleTestCase):
    @pytest.mark.skipif(
        not os.environ.get("SENDGRID_API_KEY"),
        reason="requires SENDGRID_API_KEY env var",
    )
    def test_post(self):
        """
        Sends a POST to sendgrid's live API using a private API key that is stored
        in github.
        """

        SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")

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
            self.assertEqual(val, 1)
