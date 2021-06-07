#!/usr/bin/env bash

set -ex

(
  # Build base fdk build and runtime images
  ./internal/build-scripts/build_base_image.sh 3.6
  ./internal/build-scripts/build_base_image.sh 3.7
  ./internal/build-scripts/build_base_image.sh 3.7.1
  ./internal/build-scripts/build_base_image.sh 3.8
  ./internal/build-scripts/build_base_image.sh 3.8.5
)
