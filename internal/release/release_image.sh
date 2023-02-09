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

set -xe

if [ -z "$1" ];then
  echo "Please supply python runtime version as argument to release image." >> /dev/stderr
  exit 2
fi

pyversion=$1
user="fnproject"
image="python"
OCIR_REPO=iad.ocir.io/oraclefunctionsdevelopm
ARTIFACTORY_REPO=odo-docker-signed-local.artifactory.oci.oraclecorp.com:443

echo "Pushing release images for Python Runtime Version ${pyversion}"

./regctl image copy ${OCIR_REGION}/${OCIR_LOC}/pythonfdk:${pyversion}-${BUILD_VERSION}-dev ${OCIR_REPO}/${user}/${image}:${pyversion}-dev
./regctl image copy ${OCIR_REGION}/${OCIR_LOC}/pythonfdk:${pyversion}-${BUILD_VERSION}-dev ${ARTIFACTORY_REPO}/${user}/${image}:${pyversion}-dev

./regctl image copy ${OCIR_REGION}/${OCIR_LOC}/pythonfdk:${pyversion}-${BUILD_VERSION} ${OCIR_REPO}/${user}/${image}:${pyversion}
./regctl image copy ${OCIR_REGION}/${OCIR_LOC}/pythonfdk:${pyversion}-${BUILD_VERSION} ${ARTIFACTORY_REPO}/${user}/${image}:${pyversion}