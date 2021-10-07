#!/usr/bin/env bash
#
# Copyright (c) 2019, 2020 Oracle and/or its affiliates. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
set -ex

if [[ "$BUILD_VERSION" == *"SNAPSHOT"* ]]; then
  echo "Releases will not be performed for snapshot versions, aborting."
  exit 0
fi

RUN_TYPE=${RUN_TYPE:-dry-run}
export RUN_TYPE

# Deploying images to dockerhub
if [ "${RUN_TYPE}" = "release" ]; then
  # Release base fdk build and runtime images
  echo "Deploying fdk python build and runtime images to dockerhub."
  set +x
  echo "${DOCKER_PASS}" | docker login -u "${DOCKER_USER}" --password-stdin
  set -x
  ./internal/release/release_image.sh 3.6
  ./internal/release/release_image.sh 3.7
  ./internal/release/release_image.sh 3.7.1
  ./internal/release/release_image.sh 3.8
  ./internal/release/release_image.sh 3.8.5
fi