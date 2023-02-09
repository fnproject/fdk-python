#!/usr/bin/env bash
set -ex

# The cached images will be removed as part of cleanup if not downloaded again within a particular time frame, currently set to 6 days.
docker pull container-registry.oracle.com/os/oraclelinux:8-slim
