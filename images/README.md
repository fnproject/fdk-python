Image on Docker Hub: https://hub.docker.com/r/fnproject/python

## Building Python images

```sh
pushd build/3.6; docker build -t fnproject/python:3.6-dev .; popd
pushd build/3.7; docker build -t fnproject/python:3.7-dev .; popd

pushd runtime/3.6; docker build -t fnproject/python:3.6 .; popd
pushd runtime/3.7; docker build -t fnproject/python:3.7 .; popd
```

Then push:

```sh
docker push fnproject/python:3.6-dev
docker push fnproject/python:3.6

docker push fnproject/python:3.7-dev
docker push fnproject/python:3.7
```
