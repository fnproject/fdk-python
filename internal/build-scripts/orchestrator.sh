#!/usr/bin/env bash

set -ex

BUILD_VERSION=${BUILD_VERSION:-1.0.0-SNAPSHOT}
LOCAL=${LOCAL:-true}

export BUILD_VERSION
export LOCAL

(
  # Execute unit tests
  source internal/build-scripts/execute_unit_tests.sh
)

(
  # Build dist package containing src and wheel files
  source internal/build-scripts/build_dist_pkg.sh
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

