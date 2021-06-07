#
# Copyright (c) 2019, 2020 Oracle and/or its affiliates. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os

from fdk import constants


def get_delayed_module_init_class():
    if constants.is_py37():
        return Python37DelayedImport
    else:
        return Python35plusDelayedImport


class PythonDelayedImportAbstraction(object):

    def __init__(self, func_module_path):
        self._mod_path = func_module_path
        self._executed = False

    @property
    def executed(self):
        return self._executed

    @executed.setter
    def executed(self, exec_flag):
        self._executed = exec_flag

    def get_module(self):
        raise Exception("Not implemented")


class Python35plusDelayedImport(PythonDelayedImportAbstraction):

    def __init__(self, func_module_path):
        self._func_module = None
        super(Python35plusDelayedImport, self).__init__(func_module_path)

    def get_module(self):
        if not self.executed:
            from importlib.machinery import SourceFileLoader
            fname, ext = os.path.splitext(
                os.path.basename(self._mod_path))
            self._func_module = SourceFileLoader(fname, self._mod_path)\
                .load_module()
            self.executed = True

        return self._func_module


class Python37DelayedImport(PythonDelayedImportAbstraction):

    def import_from_source(self):
        from importlib import util
        func_module_spec = util.spec_from_file_location(
            "func", self._mod_path
        )
        func_module = util.module_from_spec(func_module_spec)
        self._func_module_spec = func_module_spec
        self._func_module = func_module

    def get_module(self):
        if not self.executed:
            self.import_from_source()
            self._func_module_spec.loader.exec_module(
                self._func_module)
            self.executed = True

        return self._func_module


class Function(object):

    def __init__(self, func_module_path, entrypoint="handler"):
        dm = get_delayed_module_init_class()
        self._delayed_module_class = dm(func_module_path)
        self._entrypoint = entrypoint

    def handler(self):
        mod = self._delayed_module_class.get_module()
        return getattr(mod, self._entrypoint)
