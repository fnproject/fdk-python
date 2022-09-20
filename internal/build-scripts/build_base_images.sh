#!/usr/bin/env bash

set -ex

(
  #Create the builder instance
  docker buildx rm builderInstance || true
  docker buildx create --name builderInstance --driver docker-container --platform linux/amd64,linux/arm64
  docker buildx use builderInstance

  # Build base fdk build and runtime images
  ./internal/build-scripts/build_base_image.sh 3.6
  ./internal/build-scripts/build_base_image.sh 3.7
  ./internal/build-scripts/build_base_image.sh 3.7.1
  ./internal/build-scripts/build_base_image.sh 3.8
  ./internal/build-scripts/build_base_image.sh 3.8.5
  ./internal/build-scripts/build_base_image.sh 3.9
)
