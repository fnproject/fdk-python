#!/usr/bin/env bash
set -ex

PYTHON_3_VERSION=${PYTHON_3_VERSION:-3.9.2}

# This script is to setup python environment in teamcity agent for python fdk build pipeline.

# Install sqlite3 lib
wget http://www.sqlite.org/sqlite-autoconf-3070603.tar.gz --no-check-certificate --directory-prefix="$HOME/.sqlite-download"

pushd "$HOME/.sqlite-download"
tar xvfz sqlite-autoconf-3070603.tar.gz
pushd sqlite-autoconf-3070603
./configure --prefix="$HOME/.local"
make
make install
popd
popd

# Set up python3 pyenv(default version - v3.9.2)
echo "Setup python environment"
curl -L https://raw.githubusercontent.com/yyuu/pyenv-installer/master/bin/pyenv-installer | bash

echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init --path)"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc

source ~/.bashrc

PYTHON_CONFIGURE_OPTS="LD_RUN_PATH=$HOME/.local/lib LDFLAGS=-L$HOME/.local/lib CPPFLAGS=-I$HOME/.local/include" pyenv install ${PYTHON_3_VERSION} -s
pyenv global ${PYTHON_3_VERSION}

echo "Python Version"
python --version
