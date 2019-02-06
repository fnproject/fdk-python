Image on Docker Hub: https://hub.docker.com/r/fnproject/python

## Building Python images

```sh
pushd build/3.7.1; docker build -t fnproject/python:3.7.1-dev .; popd
pushd runtime/3.7.1; docker build -t fnproject/python:3.7.1 .; popd
```

Then push:

```sh
docker push fnproject/python:3.7.1-dev
docker push fnproject/python:3.7.1
```
