.. |travis| image:: https://travis-ci.org/sklarsa/django-sendgrid-v4.svg?branch=master

How to Install
--------------

1. `pip install django-sendgrid-v4`
2. In your project's `settings.py` script:

 	a. Set `EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"`
 	b. Add `SENDGRID_API_KEY = os.environ["SENDGRID_API_KEY"]`
