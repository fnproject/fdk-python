#!/usr/bin/env bash
set -ex

(
  python3.8 -m venv unit-test-env && . unit-test-env/bin/activate
  echo "Python Version"
  python --version
  pip3 install --upgrade pip
  pip3 install tox
  pip3 install -r requirements.txt
  tox -epep8  # Check for style guide violations if any
  tox -epy3.8 # Execute unit tests
  deactivate
  rm -rf unit-test-env
)




