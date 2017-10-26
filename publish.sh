#!/bin/bash

set -eo pipefail

rm dist/*

python setup.py sdist
python setup.py bdist_wheel --universal

twine upload dist/*
