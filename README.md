# django-sendgrid-v5

[![Latest Release](https://img.shields.io/pypi/v/django-sendgrid-v5.svg)](https://pypi.python.org/pypi/django-sendgrid-v5/)

This package implements an email backend for Django that relies on sendgrid's REST API for message delivery.

It is under active development, and pull requests are more than welcome\!

To use the backend, simply install the package (using pip), set the `EMAIL_BACKEND` setting in Django, and add a `SENDGRID_API_KEY` key (set to the appropriate value) to your Django settings.

## How to Install

1. `pip install django-sendgrid-v5`
2. In your project's settings.py script:
    1. Set `EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"`
    2. Set the SENDGRID\_API\_KEY in settings.py to your api key that was provided to you by sendgrid. `SENDGRID_API_KEY = os.environ["SENDGRID_API_KEY"]`

### Other settings

1. To toggle sandbox mode (when django is running in DEBUG mode), set `SENDGRID_SANDBOX_MODE_IN_DEBUG = True/False`.
    1. To err on the side of caution, this defaults to True, so emails sent in DEBUG mode will not be delivered, unless this setting is explicitly set to False.
2. `SENDGRID_ECHO_TO_STDOUT` will echo to stdout or any other file-like
    object that is passed to the backend via the `stream` kwarg.
3. `SENDGRID_TRACK_EMAIL_OPENS` - defaults to true and tracks email open events via the Sendgrid service. These events are logged in the Statistics UI, Email Activity interface, and are reported by the Event Webhook.
4. `SENDGRID_TRACK_CLICKS_HTML` - defaults to true and, if enabled in your Sendgrid account, will tracks click events on links found in the HTML message sent.
5. `SENDGRID_TRACK_CLICKS_PLAIN` - defaults to true and, if enabled in your Sendgrid account, will tracks click events on links found in the plain text message sent.

## Usage

### Simple

```python
from django.core.mail import send_mail

send_mail(
    'Subject here',
    'Here is the message.',
    'from@example.com',
    ['to@example.com'],
    fail_silently=False,
)
```

### Dynamic Template with JSON Data

First, create a [dynamic template](https://mc.sendgrid.com/dynamic-templates) and copy the ID.

```python
from django.core.mail import EmailMessage

msg = EmailMessage(
  from_email='to@example.com',
  to=['to@example.com'],
)
msg.template_id = "your-dynamic-template-id"
msg.dynamic_template_data = {
  "title": foo
}
msg.send(fail_silently=False)
```

### The kitchen sink EmailMessage (all of the supported sendgrid-specific properties)

```python
from django.core.mail import EmailMessage

msg = EmailMessage(
  from_email='to@example.com',
  to=['to@example.com'],
  cc=['cc@example.com'],
  bcc=['bcc@example.com'],
)

# Personalization custom args
# https://sendgrid.com/docs/for-developers/sending-email/personalizations/
msg.custom_args = {'arg1': 'value1', 'arg2': 'value2'}

# Reply to email address (sendgrid only supports 1 reply-to email address)
msg.reply_to = 'reply-to@example.com'

# Send at (accepts an integer per the sendgrid docs)
# https://sendgrid.com/docs/API_Reference/SMTP_API/scheduling_parameters.html#-Send-At
msg.send_at = 1600188812

# Transactional templates
# https://sendgrid.com/docs/ui/sending-email/how-to-send-an-email-with-dynamic-transactional-templates/
msg.template_id = "your-dynamic-template-id"
msg.dynamic_template_data = {  # Sendgrid v6+ only
  "title": foo
}
msg.substitutions = {
  "title": bar
}

# Unsubscribe groups
# https://sendgrid.com/docs/ui/sending-email/unsubscribe-groups/
msg.asm = {'group_id': 123, 'groups_to_display': ['group1', 'group2']}

# Categories
# https://sendgrid.com/docs/glossary/categories/
msg.categories = ['category1', 'category2']

# IP Pools
# https://sendgrid.com/docs/ui/account-and-settings/ip-pools/
msg.ip_pool_name = 'my-ip-pool'


msg.send(fail_silently=False)
```

## Examples

- Marcelo Canina [(@marcanuy)](https://github.com/marcanuy) wrote a great article demonstrating how to integrate `django-sendgrid-v5` into your Django application on his site: [https://simpleit.rocks/python/django/adding-email-to-django-the-easiest-way/](https://simpleit.rocks/python/django/adding-email-to-django-the-easiest-way/)
