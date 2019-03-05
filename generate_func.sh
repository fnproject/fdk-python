#!/usr/bin/env bash

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
