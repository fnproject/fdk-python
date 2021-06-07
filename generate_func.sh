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


set -xe

PY_VERSION=$(python -c "import sys; print('{}.{}'.format(sys.version_info.major, sys.version_info.minor))")

pip${PY_VERSION} install -r requirements.txt -r test-requirements.txt
pip${PY_VERSION} install wheel

python${PY_VERSION} setup.py bdist_wheel

rm -fr test_function
fn init --runtime python test_function || true

echo "build_image: fnproject/python:${PY_VERSION}-dev" >> test_function/func.yaml
echo "run_image: fnproject/python:${PY_VERSION}" >> test_function/func.yaml

pip${PY_VERSION} download -r test_function/requirements.txt -d test_function/.pip_cache

rm -fr test_function/.pip_cache/fdk*
mv dist/fdk-* test_function/.pip_cache

fn create app test-function || true
pushd test_function && fn --verbose deploy --app test-function --local --no-bump; popd
