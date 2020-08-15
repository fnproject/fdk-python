#!/usr/bin/env bash

user="fnproject"
image="python"

runtime36="3.6"
docker push ${user}/${image}:${runtime36}
docker push ${user}/${image}:${runtime36}-dev

runtime371="3.7.1"
docker push ${user}/${image}:${runtime371}
docker push ${user}/${image}:${runtime371}-dev

runtime385="3.8.5"
docker push ${user}/${image}:${runtime385}
docker push ${user}/${image}:${runtime385}-dev
