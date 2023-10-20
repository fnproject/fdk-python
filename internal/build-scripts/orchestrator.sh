#!/usr/bin/env bash

set -ex

BUILD_VERSION=${BUILD_VERSION:-1.0.0-SNAPSHOT}
LOCAL=${LOCAL:-true}

export BUILD_VERSION
export LOCAL

# Update buildx and prepare builderInstance
./internal/build-scripts/init-buildx.sh

(
  # Execute unit tests
  docker build -t fdk_python_env_image -f ./internal/docker-files/Dockerfile_TC .
  docker run --rm fdk_python_env_image ./internal/build-scripts/execute_unit_tests.sh
)

(
  # Build dist package containing src and wheel files
  docker build -t fdk_python_build_image -f ./internal/docker-files/Dockerfile_dist_pkg .
  docker run --rm -v $PWD:/build -w /build --env BUILD_VERSION=${BUILD_VERSION} fdk_python_build_image ./internal/build-scripts/build_dist_pkg.sh
)

(
  # Build base fdk build and runtime
  source internal/build-scripts/build_base_images.sh
)

(
  # Build the test integration images
  source internal/build-scripts/build_test_images.sh
)

(
  # Build RPM file
  source internal/build-scripts/rpm/create_rpms.sh
)

(
  # Perform cleanup as necessary
  source internal/build-scripts/cleanup.sh
)

