import base64
import sys
from email.mime.image import MIMEImage

from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.test import override_settings
from django.test.testcases import SimpleTestCase

from sendgrid_backend.mail import SendgridBackend
from sendgrid_backend.util import SENDGRID_5


class TestMailGeneration(SimpleTestCase):

    # Any assertDictEqual failures will show the entire diff instead of just a snippet
    maxDiff = None

    @classmethod
    def setUpClass(self):
        super(TestMailGeneration, self).setUpClass()
        with override_settings(
            EMAIL_BACKEND="sendgrid_backend.SendgridBackend",
            SENDGRID_API_KEY="DUMMY_API_KEY",
        ):
            self.backend = SendgridBackend()

    def test_EmailMessage(self):
        """
        Tests that an EmailMessage object is properly serialized into the format
        expected by Sendgrid's API
        """
        msg = EmailMessage(
            subject="Hello, World!",
            body="Hello, World!",
            from_email="Sam Smith <sam.smith@example.com>",
            to=["John Doe <john.doe@example.com>", "jane.doe@example.com"],
            cc=["Stephanie Smith <stephanie.smith@example.com>"],
            bcc=["Sarah Smith <sarah.smith@example.com>"],
            reply_to=["Sam Smith <sam.smith@example.com>"],
        )

        result = self.backend._build_sg_mail(msg)
        expected = {
            "personalizations": [
                {
                    "to": [
                        {"email": "john.doe@example.com", "name": "John Doe"},
                        {
                            "email": "jane.doe@example.com",
                        },
                    ],
                    "cc": [
                        {
                            "email": "stephanie.smith@example.com",
                            "name": "Stephanie Smith",
                        }
                    ],
                    "bcc": [
                        {"email": "sarah.smith@example.com", "name": "Sarah Smith"}
                    ],
                    "subject": "Hello, World!",
                }
            ],
            "from": {"email": "sam.smith@example.com", "name": "Sam Smith"},
            "mail_settings": {"sandbox_mode": {"enable": False}},
            "reply_to": {"email": "sam.smith@example.com", "name": "Sam Smith"},
            "subject": "Hello, World!",
            "tracking_settings": {
                "click_tracking": {"enable": True, "enable_text": True},
                "open_tracking": {"enable": True},
            },
            "content": [{"type": "text/plain", "value": "Hello, World!"}],
        }

        self.assertDictEqual(result, expected)

    def test_EmailMessage_attributes(self):
        """
        Test that send_at and categories attributes are correctly written through to output.
        """
        msg = EmailMessage(
            subject="Hello, World!",
            body="Hello, World!",
            from_email="Sam Smith <sam.smith@example.com>",
            to=["John Doe <john.doe@example.com>", "jane.doe@example.com"],
        )

        # Set new attributes as message property
        msg.send_at = 1518108670
        if SENDGRID_5:
            msg.categories = ["mammal", "dog"]
        else:
            msg.categories = ["dog", "mammal"]

        msg.ip_pool_name = "some-name"

        result = self.backend._build_sg_mail(msg)
        expected = {
            "personalizations": [
                {
                    "to": [
                        {"email": "john.doe@example.com", "name": "John Doe"},
                        {
                            "email": "jane.doe@example.com",
                        },
                    ],
                    "subject": "Hello, World!",
                    "send_at": 1518108670,
                }
            ],
            "from": {"email": "sam.smith@example.com", "name": "Sam Smith"},
            "mail_settings": {"sandbox_mode": {"enable": False}},
            "subject": "Hello, World!",
            "tracking_settings": {
                "click_tracking": {"enable": True, "enable_text": True},
                "open_tracking": {"enable": True},
            },
            "content": [{"type": "text/plain", "value": "Hello, World!"}],
            "categories": ["mammal", "dog"],
            "ip_pool_name": "some-name",
        }

        self.assertDictEqual(result, expected)

    def test_EmailMultiAlternatives(self):
        """
        Tests that django's EmailMultiAlternatives class works as expected.
        """
        msg = EmailMultiAlternatives(
            subject="Hello, World!",
            body=" ",
            from_email="Sam Smith <sam.smith@example.com>",
            to=["John Doe <john.doe@example.com>", "jane.doe@example.com"],
            cc=["Stephanie Smith <stephanie.smith@example.com>"],
            bcc=["Sarah Smith <sarah.smith@example.com>"],
            reply_to=["Sam Smith <sam.smith@example.com>"],
        )

        msg.attach_alternative("<body<div>Hello World!</div></body>", "text/html")

        # Test CSV attachment
        msg.attach("file.csv", "1,2,3,4", "text/csv")
        result = self.backend._build_sg_mail(msg)
        expected = {
            "personalizations": [
                {
                    "to": [
                        {"email": "john.doe@example.com", "name": "John Doe"},
                        {
                            "email": "jane.doe@example.com",
                        },
                    ],
                    "cc": [
                        {
                            "email": "stephanie.smith@example.com",
                            "name": "Stephanie Smith",
                        }
                    ],
                    "bcc": [
                        {"email": "sarah.smith@example.com", "name": "Sarah Smith"}
                    ],
                    "subject": "Hello, World!",
                }
            ],
            "from": {"email": "sam.smith@example.com", "name": "Sam Smith"},
            "mail_settings": {"sandbox_mode": {"enable": False}},
            "reply_to": {"email": "sam.smith@example.com", "name": "Sam Smith"},
            "subject": "Hello, World!",
            "tracking_settings": {
                "click_tracking": {"enable": True, "enable_text": True},
                "open_tracking": {"enable": True},
            },
            "attachments": [
                {"content": "MSwyLDMsNA==", "filename": "file.csv", "type": "text/csv"}
            ],
            "content": [
                {
                    "type": "text/plain",
                    "value": " ",
                },
                {
                    "type": "text/html",
                    "value": "<body<div>Hello World!</div></body>",
                },
            ],
        }

        self.assertDictEqual(result, expected)

    def test_EmailMultiAlternatives__unicode_attachment(self):
        """
        Tests that django's EmailMultiAlternatives class works as expected with a unicode-formatted
        attachment.
        """
        msg = EmailMultiAlternatives(
            subject="Hello, World!",
            body=" ",
            from_email="Sam Smith <sam.smith@example.com>",
            to=["John Doe <john.doe@example.com>", "jane.doe@example.com"],
            cc=["Stephanie Smith <stephanie.smith@example.com>"],
            bcc=["Sarah Smith <sarah.smith@example.com>"],
            reply_to=["Sam Smith <sam.smith@example.com>"],
        )
        msg.attach_alternative("<body<div>Hello World!</div></body>", "text/html")

        # Test CSV attachment
        attachments = [
            ("file.xls", b"\xd0", "application/vnd.ms-excel"),
            ("file.csv", b"C\xc3\xb4te d\xe2\x80\x99Ivoire", "text/csv"),
        ]

        if SENDGRID_5:
            for a in attachments:
                msg.attach(*a)
        else:
            for a in reversed(attachments):
                msg.attach(*a)

        result = self.backend._build_sg_mail(msg)
        expected = {
            "personalizations": [
                {
                    "to": [
                        {"email": "john.doe@example.com", "name": "John Doe"},
                        {
                            "email": "jane.doe@example.com",
                        },
                    ],
                    "cc": [
                        {
                            "email": "stephanie.smith@example.com",
                            "name": "Stephanie Smith",
                        }
                    ],
                    "bcc": [
                        {"email": "sarah.smith@example.com", "name": "Sarah Smith"}
                    ],
                    "subject": "Hello, World!",
                }
            ],
            "from": {"email": "sam.smith@example.com", "name": "Sam Smith"},
            "mail_settings": {"sandbox_mode": {"enable": False}},
            "reply_to": {"email": "sam.smith@example.com", "name": "Sam Smith"},
            "subject": "Hello, World!",
            "tracking_settings": {
                "click_tracking": {"enable": True, "enable_text": True},
                "open_tracking": {"enable": True},
            },
            "attachments": [
                {
                    "content": "0A==",
                    "filename": "file.xls",
                    "type": "application/vnd.ms-excel",
                },
                {
                    "content": "Q8O0dGUgZOKAmUl2b2lyZQ==",
                    "filename": "file.csv",
                    "type": "text/csv",
                },
            ],
            "content": [
                {
                    "type": "text/plain",
                    "value": " ",
                },
                {
                    "type": "text/html",
                    "value": "<body<div>Hello World!</div></body>",
                },
            ],
        }

        self.assertDictEqual(result, expected)

    def test_reply_to(self):
        """
        Tests reply-to functionality
        """
        kwargs = {
            "subject": "Hello, World!",
            "body": "Hello, World!",
            "from_email": "Sam Smith <sam.smith@example.com>",
            "to": ["John Doe <john.doe@example.com>"],
            "reply_to": ["Sam Smith <sam.smith@example.com>"],
            "headers": {"Reply-To": "Stephanie Smith <stephanie.smith@example.com>"},
        }

        # Test different values in Reply-To header and reply_to prop
        msg = EmailMessage(**kwargs)
        with self.assertRaises(ValueError):
            self.backend._build_sg_mail(msg)

        # Test different names (but same email) in Reply-To header and reply_to prop
        kwargs["headers"] = {"Reply-To": "Bad Name <sam.smith@example.com>"}
        msg = EmailMessage(**kwargs)
        with self.assertRaises(ValueError):
            self.backend._build_sg_mail(msg)

        # Test same name/email in both Reply-To header and reply_to prop
        kwargs["headers"] = {"Reply-To": "Sam Smith <sam.smith@example.com>"}
        msg = EmailMessage(**kwargs)
        result = self.backend._build_sg_mail(msg)
        self.assertDictEqual(
            result["reply_to"], {"email": "sam.smith@example.com", "name": "Sam Smith"}
        )

    def test_mime(self):
        """
        Tests MIMEImage support for the EmailMultiAlternatives class
        """
        msg = EmailMultiAlternatives(
            subject="Hello, World!",
            body=" ",
            from_email="Sam Smith <sam.smith@example.com>",
            to=["John Doe <john.doe@example.com>", "jane.doe@example.com"],
        )

        content = '<body><img src="cid:linux_penguin" /></body>'
        msg.attach_alternative(content, "text/html")
        with open("test/linux-penguin.png", "rb") as f:
            img = MIMEImage(f.read())
            img.add_header("Content-ID", "<linux_penguin>")
            msg.attach(img)

        result = self.backend._build_sg_mail(msg)
        self.assertEqual(len(result["content"]), 2)
        self.assertDictEqual(result["content"][0], {"type": "text/plain", "value": " "})
        self.assertDictEqual(
            result["content"][1], {"type": "text/html", "value": content}
        )
        self.assertEqual(len(result["attachments"]), 1)
        self.assertEqual(result["attachments"][0]["content_id"], "linux_penguin")

        with open("test/linux-penguin.png", "rb") as f:
            self.assertEqual(
                bytearray(result["attachments"][0]["content"], "utf-8"),
                base64.b64encode(f.read()),
            )
        self.assertEqual(result["attachments"][0]["type"], "image/png")

    def test_templating_sendgrid_v5(self):
        """
        Tests that basic templating functionality works.  This is a simple check and
        the results are valid for both Sendgrid versions 5 and 6.
        """
        msg = EmailMessage(
            subject="Hello, World!",
            body="Hello, World!",
            from_email="Sam Smith <sam.smith@example.com>",
            to=["John Doe <john.doe@example.com>", "jane.doe@example.com"],
        )
        msg.template_id = "test_template"
        result = self.backend._build_sg_mail(msg)

        self.assertIn("template_id", result)
        self.assertEquals(result["template_id"], "test_template")

    def test_templating_sendgrid(self):
        """
        Tests more complex templating scenarios for versions 5 and 6 of sendgrid

        todo: break this up into separate tests
        """
        if SENDGRID_5:
            msg = EmailMessage(
                subject="Hello, World!",
                body="Hello, World!",
                from_email="Sam Smith <sam.smith@example.com>",
                to=["John Doe <john.doe@example.com>", "jane.doe@example.com"],
            )
            msg.template_id = "test_template"
            result = self.backend._build_sg_mail(msg)

            self.assertIn("template_id", result)
            self.assertEquals(result["template_id"], "test_template")
            # Testing that for sendgrid v5 the code behave in the same way
            self.assertEquals(
                result["content"], [{"type": "text/plain", "value": "Hello, World!"}]
            )
            self.assertEquals(result["subject"], "Hello, World!")
            self.assertEquals(result["personalizations"][0]["subject"], "Hello, World!")
        else:
            msg = EmailMessage(
                from_email="Sam Smith <sam.smith@example.com>",
                to=["John Doe <john.doe@example.com>", "jane.doe@example.com"],
            )
            msg.template_id = "test_template"
            msg.dynamic_template_data = {
                "subject": "Hello, World!",
                "content": "Hello, World!",
                "link": "http://hello.com",
            }
            result = self.backend._build_sg_mail(msg)

            self.assertIn("template_id", result)
            self.assertEquals(result["template_id"], "test_template")
            self.assertEquals(
                result["personalizations"][0]["dynamic_template_data"],
                msg.dynamic_template_data,
            )
            # Subject and content should not be between request param
            self.assertNotIn("subject", result)
            self.assertNotIn("content", result)

    def test_asm(self):
        """
        Tests that unsubscribe group functionality works
        """
        msg = EmailMessage(
            subject="Hello, World!",
            body="Hello, World!",
            from_email="Sam Smith <sam.smith@example.com>",
            to=["John Doe <john.doe@example.com>", "jane.doe@example.com"],
        )
        msg.asm = {"group_id": 1}
        result = self.backend._build_sg_mail(msg)

        self.assertIn("asm", result)
        self.assertIn("group_id", result["asm"])

        del msg.asm["group_id"]
        with self.assertRaises(KeyError):
            self.backend._build_sg_mail(msg)

        msg.asm = {"group_id": 1, "groups_to_display": [2, 3, 4], "bad_key": None}
        result = self.backend._build_sg_mail(msg)

        self.assertIn("asm", result)
        self.assertIn("group_id", result["asm"])
        self.assertIn("groups_to_display", result["asm"])

    def test_EmailMessage_custom_args(self):
        """
        Tests that the custom_args property is serialized correctly
        """
        msg = EmailMessage(
            subject="Hello, World!",
            body="Hello, World!",
            from_email="Sam Smith <sam.smith@example.com>",
            to=["John Doe <john.doe@example.com>", "jane.doe@example.com"],
            cc=["Stephanie Smith <stephanie.smith@example.com>"],
            bcc=["Sarah Smith <sarah.smith@example.com>"],
            reply_to=["Sam Smith <sam.smith@example.com>"],
        )
        msg.custom_args = {"arg_1": "Foo", "arg_2": "bar"}

        result = self.backend._build_sg_mail(msg)
        expected = {
            "personalizations": [
                {
                    "to": [
                        {"email": "john.doe@example.com", "name": "John Doe"},
                        {
                            "email": "jane.doe@example.com",
                        },
                    ],
                    "cc": [
                        {
                            "email": "stephanie.smith@example.com",
                            "name": "Stephanie Smith",
                        }
                    ],
                    "bcc": [
                        {"email": "sarah.smith@example.com", "name": "Sarah Smith"}
                    ],
                    "subject": "Hello, World!",
                    "custom_args": {"arg_1": "Foo", "arg_2": "bar"},
                }
            ],
            "from": {"email": "sam.smith@example.com", "name": "Sam Smith"},
            "mail_settings": {"sandbox_mode": {"enable": False}},
            "reply_to": {"email": "sam.smith@example.com", "name": "Sam Smith"},
            "subject": "Hello, World!",
            "tracking_settings": {
                "click_tracking": {"enable": True, "enable_text": True},
                "open_tracking": {"enable": True},
            },
            "content": [{"type": "text/plain", "value": "Hello, World!"}],
        }

        self.assertDictEqual(result, expected)

    """
    todo: Implement these
    def test_attachments(self):
        pass

    def test_headers(self):
        pass

    """
