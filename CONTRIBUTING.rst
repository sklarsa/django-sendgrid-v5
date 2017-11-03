.. code-block:: bash
   :name: install_script
   cd django-sendgrid-v5
   virtualenv venv
   source venv/bin/activate
   pip install -r dev-requirements.txt
   pip install -e .

Contributing
============

Installing the development environment
--------------------------------------

1. Clone the repo :code:`git clone https://github.com/sklarsa/django-sendgrid-v5.git`

2. Create a virtual environment and install the dev-requirements.txt |install_script|

3. Run the unit tests :code:`nosetests -c nose.cfg`
