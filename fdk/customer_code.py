# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


class Function(object):

    def __init__(self, func_module_path, entrypoint="handler"):
        self.spec, self.mod = self.import_from_source(func_module_path)
        self._executed = False
        self._entrypoint = entrypoint

    @staticmethod
    def import_from_source(func_module_path):
        from importlib import util
        func_module_spec = util.spec_from_file_location(
            "func", func_module_path
        )
        func_module = util.module_from_spec(func_module_spec)
        return func_module_spec, func_module

    def handler(self):
        if self._executed is False:
            self.spec.loader.exec_module(self.mod)
            self._executed = True

        return getattr(self.mod, self._entrypoint)
