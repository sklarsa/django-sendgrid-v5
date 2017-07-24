import unittest

from django.conf import settings
from django.core.mail import EmailMessage, EmailMultiAlternatives

from sendgrid_backend.mail import SendgridBackend


settings.configure(
    EMAIL_BACKEND="sendgrid_backend.SendgridBackend",
    SENDGRID_API_KEY="DUMMY_API_KEY",
)


class TestMailGeneration(unittest.TestCase):

    def setUp(self):
        self.backend = SendgridBackend()
        self.maxDiff = None

    def test_EmailMessage(self):
        msg = EmailMessage(
            subject="Hello, World!",
            body="Hello, World!",
            from_email="Sam Smith <sam.smith@example.com>",
            to=["John Doe <john.doe@example.com>", "jane.doe@example.com"],
            reply_to=["Sam Smith <sam.smith@example.com>"],
        )

        result = self.backend._build_sg_mail(msg)
        expected = {
            "personalizations": [{
                "to": [{
                    "email": "john.doe@example.com",
                    "name": "John Doe"
                }, {
                    "email": "jane.doe@example.com",
                }],
                "subject": "Hello, World!"
            }],
            "from": {
                "email": "sam.smith@example.com",
                "name": "Sam Smith"
            },
            "reply_to": {
                "email": "sam.smith@example.com",
                "name": "Sam Smith"
            },
            "subject": "Hello, World!",
            "content": [{
                "type": "text/plain",
                "value": "Hello, World!"
            }]
        }

        self.assertDictEqual(result, expected)

    def test_EmailMultiAlternatives(self):
        msg = EmailMultiAlternatives(
            subject="Hello, World!",
            body="",
            from_email="Sam Smith <sam.smith@example.com>",
            to=["John Doe <john.doe@example.com>", "jane.doe@example.com"],
            reply_to=["Sam Smith <sam.smith@example.com>"],
        )

        msg.attach_alternative("<body<div>Hello World!</div></body>", "text/html")
        result = self.backend._build_sg_mail(msg)
        expected = {
            "personalizations": [{
                "to": [{
                    "email": "john.doe@example.com",
                    "name": "John Doe"
                }, {
                    "email": "jane.doe@example.com",
                }],
                "subject": "Hello, World!"
            }],
            "from": {
                "email": "sam.smith@example.com",
                "name": "Sam Smith"
            },
            "reply_to": {
                "email": "sam.smith@example.com",
                "name": "Sam Smith"
            },
            "subject": "Hello, World!",
            "content": [{
                "type": "text/html",
                "value": "<body<div>Hello World!</div></body>"
            }]
        }

        self.assertDictEqual(result, expected)

    """
    todo: implement these

    def test_headers(self):
        pass

    def test_attachments(self):
        pass

    def test_mime(self):
        pass
    """

if __name__ == "__main__":
    unittest.main()
