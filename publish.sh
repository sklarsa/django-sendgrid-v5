#!/bin/bash

set -eo pipefail

if [ -d "/path/to/dir" ] ; then rm -r dist/ ; fi

python setup.py sdist
python setup.py bdist_wheel --universal

twine upload dist/*
