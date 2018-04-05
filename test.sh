#!/usr/bin/env bash

fn version

CURDIR=`pwd`

OS=$(uname -s)
if [ $OS = "Darwin" ]; then
	WORK_DIR=$(mktemp -d /tmp/temp.XXXXXX)
else
	WORK_DIR=$(mktemp -d)
fi

# test CLI and latest PYPI FDK compatibility
cd $WORK_DIR
funcname="py3-func"
mkdir $funcname
cd $funcname
fn init --name $funcname --runtime python3.6
fn deploy --local --app myapp
fn call myapp /$funcname
echo -e "\n"
echo '{"name": "John"}' | fn call myapp /$funcname


# test current FDK pull request branch stability with regular function
cd $CURDIR

echo -e "name: fdk-python
version: 0.0.1
runtime: docker
format: json
path: /test-pr-branch
" >> func.yaml

rm -fr Dockerfile
echo -e "FROM python:3.6.2

RUN mkdir /code
ADD . /code/
RUN pip3 install -r /code/requirements.txt
RUN pip3 install -e /code/

WORKDIR /code/samples/echo/async
ENTRYPOINT [\"python3\", \"func.py\"]
" >> Dockerfile

fn -v deploy --local --app myapp
fn call myapp /test-pr-branch

echo -e '\n\n\n'

rm -fr Dockerfile
echo -e "FROM python:3.6.2

RUN mkdir /code
ADD . /code/
RUN pip3 install -r /code/requirements.txt
RUN pip3 install -e /code/

WORKDIR /code/samples/echo/sync
ENTRYPOINT [\"python3\", \"func.py\"]
" >> Dockerfile

fn -v deploy --local --app myapp
fn call myapp /test-pr-branch

echo -e '\n\n\n'

rm -fr Dockerfile
echo -e "FROM python:3.6.2

RUN mkdir /code
ADD . /code/
RUN pip3 install -r /code/requirements.txt
RUN pip3 install -e /code/

WORKDIR /code/samples/echo/custom_headers
ENTRYPOINT [\"python3\", \"func.py\"]
" >> Dockerfile

fn -v deploy --local --app myapp
fn call myapp /test-pr-branch

sleep 30

docker rmi -f $(docker images py3-func --format={{.ID}}) | true
docker rmi -f $(docker images fdk-python --format={{.ID}}) | true
