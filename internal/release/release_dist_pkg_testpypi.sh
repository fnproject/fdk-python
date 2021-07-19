#!/usr/bin/env bash
set -ex

(
  python3.8 -m venv .release_pkg_testpypi_venv && source .release_pkg_testpypi_venv/bin/activate
  echo "Python Version"
  python --version
  pip3 install --upgrade pip
  pip3 install twine
  URL="https://test.pypi.org/legacy/"
  echo "Release version ${BUILD_VERSION}"
  twine upload -r custom --repository-url $URL -u "${FN_TEST_PYPI_USER}" -p "${FN_TEST_PYPI_PSWD}" dist/fdk-${BUILD_VERSION}*
  deactivate
  rm -rf .release_pkg_testpypi_venv
)