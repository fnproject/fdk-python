#!/usr/bin/env bash

set -ex

(
  #Login to OCIR.
  echo ${OCIR_PASSWORD} | docker login --username "${OCIR_USERNAME}" --password-stdin ${OCIR_REGION}

  #Create the builder instance
  docker buildx rm builderInstance || true

  #We do not need this qemu-user-static image as this was required only in python fdk 3.7 and 3.7.1 and we longer support those versions.
  #docker run --rm --privileged multiarch/qemu-user-static --reset -p yes  
  docker buildx create --name builderInstance --driver-opt=image=iad.ocir.io/oraclefunctionsdevelopm/moby/buildkit:buildx-stable-1 --platform linux/amd64,linux/arm64
  docker buildx use builderInstance

  #Teamcity uses a very old version of buildx which creates a bad request body. Pushing the images to OCIR gives a 400 bad request error. Hence, use this 
  #script to upgrade the buildx version.
  ./internal/build-scripts/update-buildx.sh

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
