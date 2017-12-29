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

import functools
import traceback
import sys

from fdk.http import response as hr
from fdk.json import response as jr


def safe(dispatcher):

    @functools.wraps(dispatcher)
    def wrapper(app, context, data=None, loop=None):
        try:
            return dispatcher(app, context, data=data, loop=loop)
        except (Exception, TimeoutError) as ex:
            traceback.print_exc(file=sys.stderr)
            status = 502 if isinstance(ex, TimeoutError) else 500
            return context.DispatchError(context, status, str(ex)).response()

    return wrapper


class RawResponse(object):

    def __init__(self, context, response_data=None,
                 headers=None, status_code=200):
        """
        Generic response object
        :param context: request context
        :type context: fdk.context.RequestContext
        :param response_data: response data
        :type response_data: object
        :param headers: response headers
        :param status_code: status code
        :type status_code: int
        """
        if context.Type() == "json":
            self.response = jr.JSONResponse(
                response_data=response_data,
                headers=headers,
                status_code=status_code)
        if context.Type() == "http":
            self.response = hr.HTTPResponse(
                status_code=status_code,
                response_data=str(response_data),
                headers=headers,
                http_proto_version=context.Arguments().get(
                    "http_version"))

    def status(self):
        return self.response.status_code

    def body(self):
        return self.response.response_data

    def dump(self, stream, flush=True):
        return self.response.dump(stream, flush=flush)
