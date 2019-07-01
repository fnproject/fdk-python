#!/bin/bash
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
