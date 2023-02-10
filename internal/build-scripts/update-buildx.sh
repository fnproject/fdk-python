#!/usr/bin/env bash

set -eux

version="v0.10.0"

mkdir -p ~/.docker/cli-plugins
wget -O ~/.docker/cli-plugins/docker-buildx https://github.com/docker/buildx/releases/download/${version}/buildx-${version}.linux-amd64

chmod +x ~/.docker/cli-plugins/docker-buildx

echo "Docker buildx version"
docker buildx version