# django-sendgrid-v5
[![Latest Release](https://img.shields.io/pypi/v/django-sendgrid-v5.svg)](https://pypi.python.org/pypi/django-sendgrid-v5/) [![Travis Build Status](https://travis-ci.org/sklarsa/django-sendgrid-v5.svg)](https://travis-ci.org/sklarsa/django-sendgrid-v5) 

This package implements an email backend for Django that relies on sendgrid's REST API for message delivery.

It is under active development, and pull requests are more than welcome\!

To use the backend, simply install the package (using pip), set the `EMAIL_BACKEND` setting in Django, and add a `SENDGRID_API_KEY` key (set to the appropriate value) to your Django settings.

## How to Install                                                                                                            

1.  `pip install django-sendgrid-v5`
2.  In your project's settings.py script:
    1.  Set `EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"`
    2.  Set the SENDGRID\_API\_KEY in settings.py to your api key that was provided to you be sendgrid. `SENDGRID_API_KEY = os.environ["SENDGRID_API_KEY"]`

### Other settings

1.  To toggle sandbox mode (when django is running in DEBUG mode), set `SENDGRID_SANDBOX_MODE_IN_DEBUG = True/False`.
    1.  To err on the side of caution, this defaults to True, so emails sent in DEBUG mode will not be delivered, unless this setting is explicitly set to False.
