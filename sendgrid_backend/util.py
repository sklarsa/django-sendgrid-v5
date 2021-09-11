from typing import Any, Dict

import sendgrid
from django.conf import settings
from sendgrid.helpers.mail import Personalization

SENDGRID_VERSION = sendgrid.__version__

SENDGRID_5 = SENDGRID_VERSION < "6"
SENDGRID_6 = SENDGRID_VERSION >= "6"


def get_django_setting(setting_str, default=None):
    """
    If the django setting exists and is set, returns the value.  Otherwise returns None.
    """
    if hasattr(settings, setting_str):
        return getattr(settings, setting_str, default)
    return default


def dict_to_personalization(data: Dict[Any, Any]) -> Personalization:
    """
    Reverses Sendgrid's Personalization.get() method to create a Personalization
    object from its emitted data structure (in the form of a Dict)
    """
    personalization = Personalization()

    properties = [
        p
        for p in dir(Personalization)
        if isinstance(getattr(Personalization, p), property)
    ]
    for attr in properties:
        if attr in ["tos", "ccs", "bccs"]:
            key = attr[:-1]  # this searches the data for ["to", "cc", "bcc"]
        else:
            key = attr

        value = data.get(key, None)

        if value:
            setattr(personalization, attr, value)
            getattr(personalization, attr)

    return personalization
