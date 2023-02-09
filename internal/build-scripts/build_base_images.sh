#!/usr/bin/env bash

set -ex

(
  #Create the builder instance
  docker buildx rm builderInstance || true
  docker run --rm --privileged multiarch/qemu-user-static --reset -p yes
  docker buildx create --name builderInstance --driver-opt=image=docker-remote.artifactory.oci.oraclecorp.com/moby/buildkit:buildx-stable-1 --platform linux/amd64,linux/arm64
  docker buildx use builderInstance

  # Build base fdk build and runtime images
  ./internal/build-scripts/build_base_image.sh 3.6
  # As OL8 does not support 3.7.x
  #./internal/build-scripts/build_base_image.sh 3.7
  #./internal/build-scripts/build_base_image.sh 3.7.1
  ./internal/build-scripts/build_base_image.sh 3.8
  # Not explicitly releasing any patch versions
  #./internal/build-scripts/build_base_image.sh 3.8.5
  ./internal/build-scripts/build_base_image.sh 3.9
)
