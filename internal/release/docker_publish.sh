#!/usr/bin/env bash

set -eu

REGCTL_BIN=regctl
# Test regctl is on path
$REGCTL_BIN --help

TEMPDIR=$(mktemp -d)
cd "${TEMPDIR}"

function cleanup {
    rm -rf "${TEMPDIR}"
}
trap cleanup EXIT

{
$REGCTL_BIN image copy iad.ocir.io/oraclefunctionsdevelopm/fnproject/python:3.11 docker.io/fnproject/python:3.11;
$REGCTL_BIN image copy iad.ocir.io/oraclefunctionsdevelopm/fnproject/python:3.11-dev docker.io/fnproject/python:3.11-dev;
$REGCTL_BIN image copy iad.ocir.io/oraclefunctionsdevelopm/fnproject/python:3.8 docker.io/fnproject/python:3.8;
$REGCTL_BIN image copy iad.ocir.io/oraclefunctionsdevelopm/fnproject/python:3.8-dev docker.io/fnproject/python:3.8-dev;
$REGCTL_BIN image copy iad.ocir.io/oraclefunctionsdevelopm/fnproject/python:3.9 docker.io/fnproject/python:3.9;
$REGCTL_BIN image copy iad.ocir.io/oraclefunctionsdevelopm/fnproject/python:3.9-dev docker.io/fnproject/python:3.9-dev;
}

