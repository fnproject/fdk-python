#!/usr/bin/env bash

set -ex
mkdir -p  /temp_rpm/rpm-package
cp -r ~/rpmbuild/RPMS/x86_64/*  /temp_rpm/rpm-package
cp -r ~/rpmbuild/SRPMS/*  /temp_rpm/rpm-package