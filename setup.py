from codecs import open
from os import path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

__version__ = None
with open("sendgrid_backend/version.py") as f:
    exec(f.read())

setup(
    name="django-sendgrid-v5",
    version=str(__version__),
    description="An implementation of Django's EmailBackend compatible with sendgrid-python v5+",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sklarsa/django-sendgrid-v5",
    license="MIT",
    author="Steven Sklar",
    author_email="sklarsa@gmail.com",
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    keywords="django email sendgrid backend",
    packages=find_packages(
        exclude=[
            "test",
        ]
    ),
    install_requires=[
        "django >=1.8",
        "sendgrid >=5.0.0",
        "python-http-client >=3.0.0",
    ],
)
