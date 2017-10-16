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


class FnError(Exception):

    def __init__(self, fn_name, fn_raw_error):
        self.fn_name = fn_name
        self.fn_raw_error = fn_raw_error.decode("utf-8")
        self.message = "error at Fn: {}.".format(fn_name)

        super(FnError, self).__init__(self.message)

    def __str__(self):
        return "{}\n{}".format(self.message, self.fn_raw_error)
