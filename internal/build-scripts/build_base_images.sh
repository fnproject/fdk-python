#!/usr/bin/env bash

set -ex

(
  #Login to OCIR.
  echo ${OCIR_PASSWORD} | docker login --username "${OCIR_USERNAME}" --password-stdin ${OCIR_REGION}

  # Build base fdk build and runtime images
  ./internal/build-scripts/build_base_image.sh 3.8
  # Not explicitly releasing any patch versions
  #./internal/build-scripts/build_base_image.sh 3.8.5
  ./internal/build-scripts/build_base_image.sh 3.9
  ./internal/build-scripts/build_base_image.sh 3.11
)
