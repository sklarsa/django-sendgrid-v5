.. |travis| image:: https://travis-ci.org/sklarsa/django-sendgrid-v5.svg
             :alt: Travis Build Status
             :target: https://travis-ci.org/sklarsa/django-sendgrid-v5
.. |pypi| image:: https://img.shields.io/pypi/v/django-sendgrid-v5.svg
           :alt: Latest Release
           :target: https://pypi.python.org/pypi/django-sendgrid-v5/


django-sendgrid-v5
==================
|pypi| |travis|

This package implements an email backend for Django that relies on sendgrid's REST API for message delivery.

It is under active development, and pull requests are more than welcome!

How to Install
--------------

1. :code:`pip install django-sendgrid-v5`

2. In your project's settings.py script:

   a. Set :code:`EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"`
    
   b. Add :code:`SENDGRID_API_KEY = os.environ["SENDGRID_API_KEY"]`
