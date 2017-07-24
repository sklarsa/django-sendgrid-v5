.. |travis| image:: https://travis-ci.org/sklarsa/django-sendgrid-v4.svg
             :alt: Travis Build Status
             :target: https://travis-ci.org/sklarsa/django-sendgrid-v4
.. |pypi| image:: https://img.shields.io/pypi/v/django-sendgrid-v4.svg
           :alt: Latest Release
           :target: https://pypi.python.org/pypi/django-sendgrid-v4/


django-sendgrid-v4
==================
|pypi| |travis|

How to Install
--------------

1. `pip install django-sendgrid-v4`
2. In your project's `settings.py` script:

    a. Set `EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"`
    b. Add `SENDGRID_API_KEY = os.environ["SENDGRID_API_KEY"]`
