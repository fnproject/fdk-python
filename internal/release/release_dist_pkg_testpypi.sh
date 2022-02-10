#!/usr/bin/env bash
#
# Copyright (c) 2019, 2020 Oracle and/or its affiliates. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
set -ex

if [[ "$BUILD_VERSION" == *"SNAPSHOT"* ]]; then
  echo "Releases will not be performed for snapshot versions, aborting."
  exit 0
fi

RUN_TYPE=${RUN_TYPE:-dry-run}
export RUN_TYPE

# Release the dist source and wheel files to Test PyPi
if [ "${RUN_TYPE}" = "release" ]; then
  echo "Deploy dist source and wheel files to Test PyPi"
  python3.9 -m venv .release_pkg_testpypi_venv && source .release_pkg_testpypi_venv/bin/activate
  echo "Python Version"
  python --version
  pip3 install --upgrade pip
  pip3 install twine
  URL="https://test.pypi.org/legacy/"
  echo "Release version ${BUILD_VERSION} - Deploying to TestPyPI"
  twine upload -r custom --repository-url $URL -u "${FN_TEST_PYPI_USER}" -p "${FN_TEST_PYPI_PSWD}" dist/fdk-${BUILD_VERSION}*
  deactivate
  rm -rf .release_pkg_testpypi_venv
fi