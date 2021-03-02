from django.core.exceptions import ImproperlyConfigured
from django.test import override_settings
from django.test.testcases import SimpleTestCase

from sendgrid_backend.mail import SendgridBackend


class TestBackendInit(SimpleTestCase):
    @override_settings(
        EMAIL_BACKEND="sendgrid_backend.SendgridBackend", SENDGRID_API_KEY=None
    )
    def test_init_no_setting(self):
        # Tests that SENDGRID_API_KEY must be set for the SendgridBackend to initialize.
        # (or an api key must be explicitly passed to the constructor)
        backend = SendgridBackend(api_key="DUMMY_API_KEY")

        with self.assertRaises(ImproperlyConfigured):
            backend = SendgridBackend()  # noqa
