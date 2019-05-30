#!/usr/bin/env bash

set -xe

pyversion=${1:-"3.7.1"}

pushd images/build-stage/${pyversion} && docker build -t fnproject/python:${pyversion}-dev . && popd
pushd images/runtime/${pyversion} && docker build -t fnproject/python:${pyversion} . && popd
