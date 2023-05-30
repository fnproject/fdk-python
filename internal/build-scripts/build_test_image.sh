#!/usr/bin/env bash
set -ex

if [ -z "$1" ]; then
  echo "Please supply function directory to build test function image" >>/dev/stderr
  exit 2
fi

if [ -z "$2" ]; then
  echo "Please supply python version as argument to build image." >>/dev/stderr
  exit 2
fi

fn_dir=$1
py_version=$2
pkg_extension=${3:--py3-none-any.whl}
pkg_version=${BUILD_VERSION}

(
  # Build test function image for integration test.
  if [ ${pkg_extension} = "-py3-none-any.whl" ]; then
    # Replace 1.0.0-SNAPSHOT with 1.0.0_SNAPSHOT if the test function image is built against .whl file
    pkg_version=${pkg_version//-SNAPSHOT/_SNAPSHOT}
  fi

  # Copy the dist file ie .whl or .tar.gz from dist folder to the function test dir.
  cp -R dist/fdk-${pkg_version}${pkg_extension} ${fn_dir}
  pushd ${fn_dir}
  name="$(awk '/^name:/ { print $2 }' func.yaml)"

  if [ ${pkg_extension} = ".tar.gz" ]; then
    name=${name}-src
  fi

  version="$(awk '/^runtime:/ { print $2 }' func.yaml)"
  image_identifier="${version}-${BUILD_VERSION}"

  # Push to OCIR
  ocir_image="${OCIR_LOC}/${name}:${image_identifier}"

  docker buildx build --platform linux/amd64,linux/arm64 --push -t "${OCIR_REGION}/${ocir_image}" -f Build_file --build-arg PY_VERSION=${py_version} --build-arg PKG_VERSION=${pkg_version} --build-arg PKG_EXTENSION=${pkg_extension} --build-arg OCIR_REGION=${OCIR_REGION} --build-arg OCIR_LOC=${OCIR_LOC} --build-arg BUILD_VERSION=${BUILD_VERSION} .
  rm -rf fdk-${pkg_version}${pkg_extension}
  popd
)
