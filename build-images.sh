#!/usr/bin/env bash

set -xe

pyversion=${1:-"3.8.5"}

pushd images/build-stage/${pyversion} && docker build -t fnproject/python:${pyversion}-dev . && popd
pushd images/runtime/${pyversion} && docker build -t fnproject/python:${pyversion} . && popd
