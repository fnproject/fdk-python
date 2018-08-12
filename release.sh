#!/usr/bin/env bash


git checkout -b v${FDK_VERSION}-stable
git push origin v${FDK_VERSION}-stable
PBR_VERSION=${FDK_VERSION} python setup.py sdist bdist_wheel
twine upload dist/fdk-${FDK_VERSION}*
git checkout master
