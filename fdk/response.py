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

APP_JSON = "application/json"


class HTTPStreamResponse(object):
    def __init__(self, ctx, response_data=None,
                 headers=None, status_code=200):
        """
        HTTPStream response object
        :param ctx: request context
        :type ctx: fdk.context.HTTPStreamContext
        :param response_data: response data
        :type response_data: object
        :param headers: HTTP headers
        :type headers: dict
        :param status_code: HTTP status code
        :type status_code: int
        """

        self.status_code = status_code
        self.response_data = response_data if response_data else ""

        ctx.SetResponseHeaders(
            headers, status_code,
            content_type=headers.get(constants.CONTENT_TYPE)
        )
        self.ctx = ctx

    def status(self):
        return self.status_code

    def body(self):
        return self.response_data

    def context(self):
        return self.ctx


def response_class_from_context(context):
    """
    :param context: request context
    :type context: fdk.context.RequestContext
    """
    format_def = context.Format()
    if format_def == constants.HTTPSTREAM:
        return HTTPStreamResponse


class RawResponse(object):

    def __init__(self, ctx, response_data=None,
                 headers=None, status_code=200):
        cls = response_class_from_context(ctx)
        self.__resp = cls(
            ctx, response_data=response_data,
            headers=headers if headers else {},
            status_code=status_code
        )

    def status(self):
        return self.__resp.status_code

    def body(self):
        return self.__resp.response_data

    def context(self):
        return self.__resp.context()
