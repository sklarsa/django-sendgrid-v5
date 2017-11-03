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

3. Run the unit tests `nosetests -c nose.cfg`
