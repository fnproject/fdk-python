#!/usr/bin/env bash

set -xe

pyversion=${1:-"3.7.1"}

SNYK_TOKEN=${SNYK_TOKEN} snyk test --docker fnproject/python:${pyversion}-dev --file=images/build-stage/${pyversion}/Dockerfile --json | docker run --rm -i denismakogon/snyk-filter:0.0.6
SNYK_TOKEN=${SNYK_TOKEN} snyk test --docker fnproject/python:${pyversion} --file=images/runtime/${pyversion}/Dockerfile --json | docker run --rm -i denismakogon/snyk-filter:0.0.6
