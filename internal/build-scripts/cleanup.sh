#!/usr/bin/env bash

set -ex

if [ ${LOCAL} = "true" ]; then
  # Remove dist and build folders
  rm -rf dist
  rm -rf build
fi
