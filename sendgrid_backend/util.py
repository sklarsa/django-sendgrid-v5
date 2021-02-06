import sendgrid
from django.conf import settings

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
