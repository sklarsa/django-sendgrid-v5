from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="django-sendgrid-v4",
    version="0.1.2a",
    description="An implementation of Django's EmailBackend compatible with sendgrid-python v4+",
    long_description=long_description,
    url="https://github.com/sklarsa/django-sendgrid-v4",
    license="WTFPL",
    author="Steven Sklar",
    author_email="sklarsa@gmail.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
    ],
    keywords="django email sendgrid backend",
    packages=find_packages(exclude=[]),
    install_requires=["django", "sendgrid"]
)
