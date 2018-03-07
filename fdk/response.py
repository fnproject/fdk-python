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

import ujson
import functools
import traceback
import sys

from fdk import headers as hrs


class JSONResponse(object):

    def __init__(self, response_data=None, headers=None, status_code=200):
        """
        JSON response object
        :param response_data: JSON response data (dict, str)
        :type response_data: str
        :param headers: JSON response HTTP headers
        :type headers: fdk.headers.GoLikeHeaders
        :param status_code: JSON response HTTP status code
        :type status_code: int
        """
        self.status_code = status_code
        self.response_data = response_data if response_data else ""
        self.headers = hrs.GoLikeHeaders({})
        if isinstance(headers, dict):
            self.headers = hrs.GoLikeHeaders(headers)
        if isinstance(headers, hrs.GoLikeHeaders):
            self.headers = headers

    def dump(self):
        """
        Dumps raw JSON response to a stream
        :return: result of dumping
        """
        self.headers.set("content-length", len(self.response_data))
        resp = ujson.dumps({
            "body": self.response_data,
            "status_code": self.status_code,
            "headers": self.headers.for_dump()
        })
        print("Prepared response: {}".format(resp),
              file=sys.stderr, flush=True)
        print(resp, file=sys.stdout, flush=True)


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
        :type response_data: str
        :param headers: response headers
        :param status_code: status code
        :type status_code: int
        """
        self.response = JSONResponse(
            response_data=response_data,
            headers=headers,
            status_code=status_code)

    def status(self):
        return self.response.status_code

    def body(self):
        return self.response.response_data

    def dump(self):
        return self.response.dump()
