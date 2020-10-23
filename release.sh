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

set -ex

# ensure working dir is clean
git status
if [[ -z $(git status -s) ]]
then
  echo "tree is clean"
else
  echo "tree is dirty, please commit changes before running this"
  exit 1
fi

git pull

version_file="fdk/version.py"
current_version=$(grep -m1 -Eo "[0-9]+\.[0-9]+\.[0-9]+" ${version_file})
new_version=$(docker run --rm marcelocorreia/semver semver -c -i patch ${current_version})

echo "Current version: $current_version"
echo "New version: $new_version"

echo "VERSION = '${new_version}'" > fdk/version.py

tag="$new_version"
git add -u
git commit -m "FDK Python: $new_version release [skip ci]"
git tag -f -a $tag -m "version $new_version"
git push
git push origin $tag

PBR_VERSION=${new_version} python setup.py sdist bdist_wheel
twine upload -u ${FN_PYPI_USER} -p ${FN_PYPI_PSWD} dist/fdk-${new_version}*
