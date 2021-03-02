import os
import sys
import warnings
from unittest.mock import MagicMock

from django.core.mail import EmailMessage
from django.test import override_settings
from django.test.testcases import SimpleTestCase
from python_http_client.exceptions import UnauthorizedError

from sendgrid_backend.mail import SendgridBackend


class TestEchoToOutput(SimpleTestCase):
    def test_echo(self):
        settings = {
            "DEBUG": True,
            "SENDGRID_API_KEY": "DOESNT_MATTER",
            "EMAIL_BACKEND": "sendgrid_backend.SendgridBackend",
            "SENDGRID_ECHO_TO_STDOUT": True,
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
            try:
                msg.send()
            except UnauthorizedError:
                # Since Github only runs live server tests on protected branches (for security),
                # we will get an unauthorized error when attempting to hit the sendgrid api endpoint, even in
                # sandbox mode.
                warnings.warn(
                    "Sendgrid requests using sandbox mode still need valid credentials for the "
                    + "request to succeed."
                )
            self.assertTrue(mocked_output_stream.write.called)
