#!/usr/bin/env bash

set -ex

if [ "${LOCAL}" = "true" ] && [ "${RUN_TYPE}" != "release" ]; then
  # Remove dist and build folders
  rm -rf dist
  rm -rf build
fi
