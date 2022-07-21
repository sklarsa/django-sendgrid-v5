from django.core.mail import EmailMessage
from django.test import override_settings
from django.test.testcases import SimpleTestCase
from sendgrid.helpers.mail import BypassListManagement, MailSettings

from sendgrid_backend.mail import SendgridBackend


class TestSandboxMode(SimpleTestCase):
    def test_sandbox_mode(self):
        """
        Tests combinations of DEBUG, SENDGRID_SANDBOX_MODE_IN_DEBUG, and mail_settings to ensure
        that the behavior is as expected.
        """
        msg = EmailMessage(
            subject="Hello, World!",
            body="Hello, World!",
            from_email="Sam Smith <sam.smith@example.com>",
            to=["John Doe <john.doe@example.com>"],
        )
        msg_with_settings = EmailMessage(
            subject="Hello, World!",
            body="Hello, World!",
            from_email="Sam Smith <sam.smith@example.com>",
            to=["John Doe <john.doe@example.com>"],
        )
        # additional setting to test existing settings preserved then sandbox_mode populated
        mail_settings = MailSettings()
        mail_settings.bypass_list_management = BypassListManagement(enable=True)
        msg_with_settings.mail_settings = mail_settings

        # Sandbox mode should be False
        with override_settings(DEBUG=False, SENDGRID_SANDBOX_MODE_IN_DEBUG=True):
            backend = SendgridBackend(api_key="stub")

            result = backend._build_sg_mail(msg)
            self.assertIn("mail_settings", result)
            self.assertIn("sandbox_mode", result["mail_settings"])
            self.assertNotIn("bypass_list_management", result["mail_settings"])
            self.assertFalse(result["mail_settings"]["sandbox_mode"]["enable"])

        # Sandbox mode should be True
        with override_settings(DEBUG=True, SENDGRID_SANDBOX_MODE_IN_DEBUG=True):
            backend = SendgridBackend(api_key="stub")

            result = backend._build_sg_mail(msg)
            self.assertIn("mail_settings", result)
            self.assertIn("sandbox_mode", result["mail_settings"])
            self.assertNotIn("bypass_list_management", result["mail_settings"])
            self.assertTrue(result["mail_settings"]["sandbox_mode"]["enable"])

        # Sandbox mode should be True (by default when DEBUG==True)
        with override_settings(DEBUG=True):
            backend = SendgridBackend(api_key="stub")

            result = backend._build_sg_mail(msg)
            self.assertIn("mail_settings", result)
            self.assertIn("sandbox_mode", result["mail_settings"])
            self.assertNotIn("bypass_list_management", result["mail_settings"])
            self.assertTrue(result["mail_settings"]["sandbox_mode"]["enable"])

        # Sandbox mode should be False
        with override_settings(DEBUG=True, SENDGRID_SANDBOX_MODE_IN_DEBUG=False):
            backend = SendgridBackend(api_key="stub")

            result = backend._build_sg_mail(msg)
            self.assertIn("mail_settings", result)
            self.assertIn("sandbox_mode", result["mail_settings"])
            self.assertNotIn("bypass_list_management", result["mail_settings"])
            self.assertFalse(result["mail_settings"]["sandbox_mode"]["enable"])

        # Sandbox mode should be False with existing settings preserved
        with override_settings(DEBUG=False, SENDGRID_SANDBOX_MODE_IN_DEBUG=True):
            backend = SendgridBackend(api_key="stub")

            result = backend._build_sg_mail(msg_with_settings)
            self.assertIn("mail_settings", result)
            self.assertIn("sandbox_mode", result["mail_settings"])
            self.assertIn("bypass_list_management", result["mail_settings"])
            self.assertFalse(result["mail_settings"]["sandbox_mode"]["enable"])
            self.assertTrue(result["mail_settings"]["bypass_list_management"]["enable"])

        # Sandbox mode should be True with existing settings preserved
        with override_settings(DEBUG=True, SENDGRID_SANDBOX_MODE_IN_DEBUG=True):
            backend = SendgridBackend(api_key="stub")

            result = backend._build_sg_mail(msg_with_settings)
            self.assertIn("mail_settings", result)
            self.assertIn("sandbox_mode", result["mail_settings"])
            self.assertIn("bypass_list_management", result["mail_settings"])
            self.assertTrue(result["mail_settings"]["sandbox_mode"]["enable"])
            self.assertTrue(result["mail_settings"]["bypass_list_management"]["enable"])

        # Sandbox mode should be True (by default when DEBUG==True) with existing settings preserved
        with override_settings(DEBUG=True):
            backend = SendgridBackend(api_key="stub")

            result = backend._build_sg_mail(msg_with_settings)
            self.assertIn("mail_settings", result)
            self.assertIn("sandbox_mode", result["mail_settings"])
            self.assertIn("bypass_list_management", result["mail_settings"])
            self.assertTrue(result["mail_settings"]["sandbox_mode"]["enable"])
            self.assertTrue(result["mail_settings"]["bypass_list_management"]["enable"])

        # Sandbox mode should be False with existing settings preserved
        with override_settings(DEBUG=True, SENDGRID_SANDBOX_MODE_IN_DEBUG=False):
            backend = SendgridBackend(api_key="stub")

            result = backend._build_sg_mail(msg_with_settings)
            self.assertIn("mail_settings", result)
            self.assertIn("sandbox_mode", result["mail_settings"])
            self.assertIn("bypass_list_management", result["mail_settings"])
            self.assertFalse(result["mail_settings"]["sandbox_mode"]["enable"])
            self.assertTrue(result["mail_settings"]["bypass_list_management"]["enable"])
