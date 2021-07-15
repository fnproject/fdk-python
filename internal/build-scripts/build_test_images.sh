#!/usr/bin/env bash

set -ex

# Login to OCIR
echo ${OCIR_PASSWORD} | docker login --username "${OCIR_USERNAME}" --password-stdin ${OCIR_REGION}

# Build and push the test function images to OCIR for integration test framework.

# Python 3.8
(
  source internal/build-scripts/build_test_image.sh internal/tests-images/python3.8/hello-world-test 3.8
  source internal/build-scripts/build_test_image.sh internal/tests-images/python3.8/timeout-test 3.8
  source internal/build-scripts/build_test_image.sh internal/tests-images/python3.8/runtime-version-test 3.8
  source internal/build-scripts/build_test_image.sh internal/tests-images/python3.8/oci-sdk-test 3.8

  #Build hello-world-fn test image with src dist file.
  source internal/build-scripts/build_test_image.sh internal/tests-images/python3.8/hello-world-test 3.8 ".tar.gz"
)

# Python 3.7
(
  source internal/build-scripts/build_test_image.sh internal/tests-images/python3.7/runtime-version-test 3.7
)

# Python 3.6
(
  source internal/build-scripts/build_test_image.sh internal/tests-images/python3.6/runtime-version-test 3.6
)
