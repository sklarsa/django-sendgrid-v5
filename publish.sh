#!/bin/bash

set -eo pipefail

if [ -d "dist/" ] ; then rm -r dist/ ; fi

python -m build

twine upload dist/*
