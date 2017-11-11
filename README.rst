.. |travis| image:: https://travis-ci.org/sklarsa/django-sendgrid-v5.svg
             :alt: Travis Build Status
             :target: https://travis-ci.org/sklarsa/django-sendgrid-v5
.. |pypi| image:: https://img.shields.io/pypi/v/django-sendgrid-v5.svg
           :alt: Latest Release
           :target: https://pypi.python.org/pypi/django-sendgrid-v5/
.. _sandbox mode: https://sendgrid.com/docs/Classroom/Send/v3_Mail_Send/sandbox_mode.html

==================
django-sendgrid-v5
==================
|pypi| |travis|

This package implements an email backend for Django that relies on sendgrid's REST API for message delivery.

It is under active development, and pull requests are more than welcome!

To use the backend, simply install the package (using pip), set the EMAIL_BACKEND setting in Django, and add a SENDGRID_API_KEY key (set to the appropriate value) to your Django settings.


How to Install
==============

1. :code:`pip install django-sendgrid-v5`

2. In your project's settings.py script:

   a. Set :code:`EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"`

   b. Set the SENDGRID_API_KEY in settings.py to your api key that was provided to you be sendgrid.
      :code:`SENDGRID_API_KEY = os.environ["SENDGRID_API_KEY"]`


Other settings
--------------
1. To toggle "sandbox mode" (when django is running in DEBUG mode), set :code:`SENDGRID_SANDBOX_MODE_IN_DEBUG =  True/False`.  
 
     a. To err on the side of caution, this defaults to True, so emails sent in DEBUG mode will not be delievered, unless this setting is explicitly set to False.
