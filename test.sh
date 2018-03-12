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

# test current FDK pull request branch stability
cd $CURDIR
fn deploy --local --app myapp
fn call myapp /test-pr-branch
