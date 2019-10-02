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

from fdk import context
from fdk import constants


class Response(object):

    def __init__(self, ctx: context.InvokeContext,
                 response_data: str=None,
                 headers: dict=None,
                 status_code: int=200):
        """
        Creates an FDK-readable response object
        :param ctx: invoke context
        :type ctx: fdk.context.InvokeContext
        :param response_data: function's response data
        :type response_data: str
        :param headers: response headers
        :type headers: dict
        :param status_code: response code
        :type status_code: int
        """
        self.ctx = ctx
        self.status_code = status_code
        self.response_data = response_data if response_data else ""
        if headers is None:
            headers = {}
        headers.update({constants.FN_FDK_VERSION:
                        constants.VERSION_HEADER_VALUE})
        ctx.SetResponseHeaders(headers, status_code)
        self.ctx = ctx

    def status(self):
        return self.status_code

    def body(self):
        return self.response_data

    def context(self):
        return self.ctx
