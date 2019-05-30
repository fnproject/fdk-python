#!/usr/bin/env bash

user="fnproject"
image="python"
runtime36="3.6"
runtime371="3.7.1"

docker push ${user}/${image}:${runtime36}
docker push ${user}/${image}:${runtime36}-dev

docker push ${user}/${image}:${runtime371}
docker push ${user}/${image}:${runtime371}-dev
