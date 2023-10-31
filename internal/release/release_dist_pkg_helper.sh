#!/usr/bin/env bash


set -ex

if [[ "$BUILD_VERSION" == *"SNAPSHOT"* ]]; then
  echo "Releases will not be performed for snapshot versions, aborting."
  exit 0
fi

RUN_TYPE=${RUN_TYPE:-dry-run}
export RUN_TYPE

# Release the dist source and wheel files to Prod PyPi
if [ "${RUN_TYPE}" = "release" ]; then
      docker build -t fdk_python_build_image -f ./internal/docker-files/Dockerfile_dist_pkg .
      docker run --rm -v $PWD:/build -w /build --env BUILD_VERSION=${BUILD_VERSION} --env FN_PYPI_USER=${FN_PYPI_USER} --env FN_PYPI_PSWD=${FN_PYPI_PSWD} fdk_python_build_image ./internal/release/release_dist_pkg.sh
fi

