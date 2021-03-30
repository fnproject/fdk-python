Image on Docker Hub: https://hub.docker.com/r/fnproject/python

## Building Python images

```sh
pushd build-stage/3.6; docker build -t fnproject/python:3.6-dev .; popd
pushd runtime/3.6; docker build -t fnproject/python:3.6 .; popd
```

```sh
pushd build-stage/3.7.1; docker build -t fnproject/python:3.7.1-dev .; popd
pushd runtime/3.7.1; docker build -t fnproject/python:3.7.1 .; popd
```

```sh
pushd build-stage/3.7; docker build -t fnproject/python:3.7-dev .; popd
pushd runtime/3.7; docker build -t fnproject/python:3.7 .; popd
```

```sh
pushd build-stage/3.8.5; docker build -t fnproject/python:3.8.5-dev .; popd
pushd runtime/3.8.5; docker build -t fnproject/python:3.8.5 .; popd
```

```sh
pushd build-stage/3.8; docker build -t fnproject/python:3.8-dev .; popd
pushd runtime/3.8; docker build -t fnproject/python:3.8 .; popd
```

Then push:

```sh
docker push fnproject/python:3.6-dev
docker push fnproject/python:3.6
```

```sh
docker push fnproject/python:3.7.1-dev
docker push fnproject/python:3.7.1
```

```sh
docker push fnproject/python:3.7-dev
docker push fnproject/python:3.7
```

```sh
docker push fnproject/python:3.8.5-dev
docker push fnproject/python:3.8.5
```

```sh
docker push fnproject/python:3.8-dev
docker push fnproject/python:3.8
```