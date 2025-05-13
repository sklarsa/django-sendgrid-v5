from functools import wraps
from inspect import iscoroutinefunction
from typing import Callable

from django.conf import settings
from django.http import HttpResponseNotFound

from sendgrid_backend.util import SENDGRID_6

if SENDGRID_6:
    from sendgrid.helpers.eventwebhook import EventWebhook
    from sendgrid.helpers.eventwebhook.eventwebhook_header import EventWebhookHeader

    # Adapted from:
    # https://stackoverflow.com/a/71672552
    def check_sendgrid_signature(request):
        event_webhook = EventWebhook()
        key = settings.SENDGRID_WEBHOOK_VERIFICATION_KEY
        ec_public_key = event_webhook.convert_public_key_to_ecdsa(key)

        return event_webhook.verify_signature(
            request.body.decode("utf-8"),
            request.headers[EventWebhookHeader.SIGNATURE],
            request.headers[EventWebhookHeader.TIMESTAMP],
            ec_public_key,
        )

    def verify_sendgrid_webhook_signature(func: Callable) -> Callable:
        """Check a view for a valid sendgrid webhook"""
        if iscoroutinefunction(func):

            @wraps(func)
            async def inner(request, *args, **kwargs):
                if not check_sendgrid_signature(request):
                    return HttpResponseNotFound()
                return await func(request, *args, **kwargs)

        else:

            @wraps(func)
            def inner(request, *args, **kwargs):
                if not check_sendgrid_signature(request):
                    return HttpResponseNotFound()
                return func(request, *args, **kwargs)

        return inner
