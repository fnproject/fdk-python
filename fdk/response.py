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

from fdk import constants


class Response(object):

    def __init__(self, ctx, response_data=None,
                 headers=None, status_code=200):
        self.ctx = ctx
        self.status_code = status_code
        self.response_data = response_data if response_data else ""
        if headers is None:
            headers = {}
        ctx.SetResponseHeaders(
            headers, status_code,
            content_type=headers.get(
                constants.CONTENT_TYPE, "text/plain")
        )
        self.ctx = ctx

    def status(self):
        return self.status_code

    def body(self):
        return self.response_data

    def context(self):
        return self.ctx
