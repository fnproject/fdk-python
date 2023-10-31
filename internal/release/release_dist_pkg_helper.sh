#!/usr/bin/env bash

set -ex

BUILD_VERSION=${BUILD_VERSION:-1.0.0-SNAPSHOT}
LOCAL=${LOCAL:-true}

export BUILD_VERSION
export LOCAL

(
  # Release the dist source and wheel files to Prod PyPi
  docker build -t fdk_python_build_image -f ./internal/docker-files/Dockerfile_dist_pkg .
  docker run --rm -v $PWD:/build -w /build --env BUILD_VERSION=${BUILD_VERSION} fdk_python_build_image ./internal/release/release_dist_pkg.sh
)