#!/usr/bin/env bash

set -eux

# Teamcity uses a very old version of buildx which creates a bad request body. Pushing the images to OCIR gives a 400 bad request error. Hence, use this
# script to upgrade the buildx version.

version="v0.10.0"
mkdir -p ~/.docker/cli-plugins
wget -O ~/.docker/cli-plugins/docker-buildx https://github.com/docker/buildx/releases/download/${version}/buildx-${version}.linux-amd64

chmod +x ~/.docker/cli-plugins/docker-buildx

echo "Docker buildx version"
docker buildx version

#Create the builder instance
(
   docker buildx rm builderInstance || true
   docker buildx create --name builderInstance --driver-opt=image=iad.ocir.io/oraclefunctionsdevelopm/moby/buildkit:buildx-stable-1 --platform linux/amd64,linux/arm64
   docker buildx use builderInstance
)