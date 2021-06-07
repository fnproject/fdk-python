#!/usr/bin/env bash
set -ex

(
  python3.8 -m venv .dist_pkg_venv && source .dist_pkg_venv/bin/activate
  echo "Python Version"
  python --version
  pip3 install --upgrade pip
  pip3 install wheel
  PBR_VERSION=${BUILD_VERSION} python setup.py sdist bdist_wheel
  deactivate
  rm -rf .dist_pkg_venv
)
