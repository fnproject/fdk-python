#!/bin/bash
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

# This script creates sanity-testing/internal folder containing the copied over scripts from fdk-python/internal/build-scripts folder
# to be used later for sanity testing.

set -ex

# list checkout directory contents
ls -al

# Create sanity-testing/internal folder at the checkout directory
mkdir -p sanity-testing/internal/
cd sanity-testing/internal/

# Create sub directories inside sanity-testing/internal folder.
mkdir -p build-scripts
rm -rf build-scripts/*

mkdir -p release
rm -rf release/*

cd ../../

# copy required files from .bitbucket/internal folder into the sanity-testing/internal folder required for sanity testing later.
cp -R .bitbucket/internal/build-scripts/execute_unit_tests.sh sanity-testing/internal/build-scripts/execute_unit_tests.sh
cp -R .bitbucket/internal/build-scripts/build_dist_pkg.sh sanity-testing/internal/build-scripts/build_dist_pkg.sh
cp -R .bitbucket/internal/release/sanity_testing.sh sanity-testing/internal/release/sanity_testing.sh
