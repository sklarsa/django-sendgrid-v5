from unittest.mock import MagicMock

from django.http import HttpResponseNotFound
from django.test import SimpleTestCase

from sendgrid_backend.util import SENDGRID_6

if SENDGRID_6:
    from ellipticcurve.ecdsa import Ecdsa
    from ellipticcurve.privateKey import PrivateKey
    from sendgrid.helpers.eventwebhook.eventwebhook_header import EventWebhookHeader

    from sendgrid_backend.decorators import (
        check_sendgrid_signature,
        verify_sendgrid_webhook_signature,
    )

    # Generate privateKey from PEM string
    PRIVATE_KEY = PrivateKey.fromPem(
        """
        -----BEGIN EC PARAMETERS-----
        BgUrgQQACg==
        -----END EC PARAMETERS-----
        -----BEGIN EC PRIVATE KEY-----
        MHQCAQEEIODvZuS34wFbt0X53+P5EnSj6tMjfVK01dD1dgDH02RzoAcGBSuBBAAK
        oUQDQgAE/nvHu/SQQaos9TUljQsUuKI15Zr5SabPrbwtbfT/408rkVVzq8vAisbB
        RmpeRREXj5aog/Mq8RrdYy75W9q/Ig==
        -----END EC PRIVATE KEY-----
    """
    )
    PUBLIC_KEY_STRING = "".join(PRIVATE_KEY.publicKey().toPem().splitlines()[2:-1])
    TIMESTAMP = "2025-05-13 07:42:18.792332+00:00"

    class TestDecoratorTestCase(SimpleTestCase):
        @classmethod
        def setUpClass(cls):
            cls.message = "this data should be signed"

            cls.good_request = MagicMock()
            cls.good_request.body.decode.return_value = "this data should be signed"
            cls.good_request.headers = {
                EventWebhookHeader.SIGNATURE: Ecdsa.sign(
                    TIMESTAMP + cls.message, PRIVATE_KEY
                ).toBase64(),
                EventWebhookHeader.TIMESTAMP: TIMESTAMP,
            }

            cls.bad_request = MagicMock()
            cls.bad_request.body.decode.return_value = "this data should be signed"
            cls.bad_request.headers = {
                EventWebhookHeader.SIGNATURE: Ecdsa.sign(
                    TIMESTAMP + cls.message, PRIVATE_KEY
                ).toBase64(),
                EventWebhookHeader.TIMESTAMP: TIMESTAMP + "A",  # One character off
            }

        def test_check_sendgrid_signature(self):
            with self.settings(SENDGRID_WEBHOOK_VERIFICATION_KEY=PUBLIC_KEY_STRING):
                self.assertTrue(check_sendgrid_signature(self.good_request))

        def test_check_sendgrid_signature_bad_signature(self):
            with self.settings(SENDGRID_WEBHOOK_VERIFICATION_KEY=PUBLIC_KEY_STRING):
                self.assertFalse(check_sendgrid_signature(self.bad_request))

        def test_verify_sendgrid_webhook_signature_decorator(self):
            @verify_sendgrid_webhook_signature
            def test_func(request):
                return "The function was successfully run"

            with self.settings(SENDGRID_WEBHOOK_VERIFICATION_KEY=PUBLIC_KEY_STRING):
                self.assertEqual(
                    test_func(self.good_request), "The function was successfully run"
                )

        def test_verify_sendgrid_webhook_signature_decorator_bad_signature(self):
            @verify_sendgrid_webhook_signature
            def test_func(request):
                return "The function was successfully run"

            with self.settings(SENDGRID_WEBHOOK_VERIFICATION_KEY=PUBLIC_KEY_STRING):
                self.assertIsInstance(test_func(self.bad_request), HttpResponseNotFound)

        async def test_async_verify_sendgrid_webhook_signature_decorator(self):
            @verify_sendgrid_webhook_signature
            async def test_func(request):
                return "The function was successfully run"

            with self.settings(SENDGRID_WEBHOOK_VERIFICATION_KEY=PUBLIC_KEY_STRING):
                self.assertEqual(
                    await test_func(self.good_request),
                    "The function was successfully run",
                )

        async def test_async_verify_sendgrid_webhook_signature_decorator_bad_signature(
            self,
        ):
            @verify_sendgrid_webhook_signature
            async def test_func(request):
                return "The function was successfully run"

            with self.settings(SENDGRID_WEBHOOK_VERIFICATION_KEY=PUBLIC_KEY_STRING):
                self.assertIsInstance(
                    await test_func(self.bad_request), HttpResponseNotFound
                )
