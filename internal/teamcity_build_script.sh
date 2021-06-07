#!/usr/bin/env bash
set -ex

PYTHON_3_VERSION=${PYTHON_3_VERSION:-3.8.5}

# This script is to setup python environment in teamcity agent for python fdk build pipeline.

# Install sqlite3 lib
wget http://www.sqlite.org/sqlite-autoconf-3070603.tar.gz

tar xvfz sqlite-autoconf-3070603.tar.gz
pushd sqlite-autoconf-3070603
./configure --prefix="$HOME/.local"
make
make install
popd

# Set up python3 pyenv(default version - v3.8.5)
echo "Setup python environment"
curl -L https://raw.githubusercontent.com/yyuu/pyenv-installer/master/bin/pyenv-installer | bash
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv init --path)"
eval "$(pyenv virtualenv-init -)"
PYTHON_CONFIGURE_OPTS="LD_RUN_PATH=$HOME/.local/lib LDFLAGS=-L$HOME/.local/lib CPPFLAGS=-I$HOME/.local/include" pyenv install ${PYTHON_3_VERSION} -s
pyenv shell ${PYTHON_3_VERSION}

echo "Python Version"
python --version

# Invoke script to build artifacts, base fdk images and test function images.
./internal/build-scripts/orchestrator.sh
