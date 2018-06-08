Contributing
============

Installing the development environment
--------------------------------------

1. Clone the repo `git clone https://github.com/sklarsa/django-sendgrid-v5.git`

2. Create a virtual environment and install the dev-requirements.txt

   ```
   cd django-sendgrid-v5
   virtualenv venv
   source venv/bin/activate
   pip install -r dev-requirements.txt
   pip install -e .
   ```

3. If you want to run tests that post to the sendgrid API directly, you need to set an environment variable, `SENDGRID_API_KEY`.  Otherwise, related tests will fail.

4. Run the unit tests `nosetests -c nose.cfg`
