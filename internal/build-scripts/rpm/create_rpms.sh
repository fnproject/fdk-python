#!/usr/bin/env bash

set -xe
pkg_version=${BUILD_VERSION}

pkg_version=${pkg_version//-SNAPSHOT/_SNAPSHOT}

docker build -t build_rpm_36:1.0  --build-arg RPM_VERSION=${pkg_version}  -f ./internal/images/build-stage/3.6/Dockerfile-rpm .
docker run --rm -v$PWD:/temp_rpm build_rpm_36:1.0 ./create_python36_rpm.sh

docker build -t build_rpm_38:1.0   --build-arg RPM_VERSION=${pkg_version}  -f ./internal/images/build-stage/3.8/Dockerfile-rpm .
docker run --rm -v$PWD:/temp_rpm  build_rpm_38:1.0 ./create_python38_rpm.sh

