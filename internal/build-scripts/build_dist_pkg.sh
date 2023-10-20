#!/usr/bin/env bash
set -ex

(
  python3.11 -m venv .dist_pkg_venv && source .dist_pkg_venv/bin/activate
  echo "Python Version"
  python3 --version
  pip3 install --upgrade pip
  pip3 install wheel
  # use latest setuptools to include License-File Key in Metadata file inside wheel pkg.
  pip3 install setuptools>=65.7.0
  PBR_VERSION=${BUILD_VERSION} python3 setup.py sdist bdist_wheel
  deactivate
  rm -rf .dist_pkg_venv
)
