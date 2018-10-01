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

import datetime as dt
import os

from fdk import constants
from fdk import headers as hs


def set_response_headers(current_headers, new_headers,
                         status_code, content_type=None):
    if isinstance(new_headers, dict):
        new_headers = hs.GoLikeHeaders(new_headers)
    elif isinstance(new_headers, hs.GoLikeHeaders):
        pass
    else:
        raise TypeError(
            "Invalid headers type: {}, only dict allowed."
            .format(type(new_headers))
        )

    new_headers = hs.encap_headers(
        new_headers,
        status=status_code,
        content_type=content_type
    )
    for k, v in new_headers.items():
        current_headers.set(k, v)

    return current_headers


class InvokeContext(object):

    def __init__(self, app_id, fn_id, call_id,
                 content_type="application/octet-stream",
                 deadline=None, config=None,
                 headers=None, arguments=None,
                 request_url=None, method="POST",
                 fn_format=None):
        """
        Request context here to be a placeholder
        for request-specific attributes
        """
        self.__app_id = app_id
        self.__fn_id = fn_id
        self.__call_id = call_id
        self.__config = config if config else {}
        self.__headers = headers if headers else {}
        self._arguments = {} if not arguments else arguments
        self.__deadline = deadline
        self.__content_type = content_type
        self._request_url = request_url
        self._method = method
        self.__response_headers = hs.GoLikeHeaders({})
        self.__fn_format = fn_format

    def AppID(self):
        return self.__app_id

    def FnID(self):
        return self.__fn_id

    def CallID(self):
        return self.__call_id

    def Config(self):
        return self.__config

    def Headers(self):
        return self.__headers

    def Format(self):
        return self.__fn_format

    def Deadline(self):
        if self.__deadline is None:
            now = dt.datetime.now(dt.timezone.utc).astimezone()
            now += dt.timedelta(0, float(constants.DEFAULT_DEADLINE))
            return now.isoformat()
        return self.__deadline

    def SetResponseHeaders(self, headers, status_code, content_type=None):
        self.__response_headers = set_response_headers(
            self.GetResponseHeaders(), headers, status_code,
            content_type=content_type)

    def GetResponseHeaders(self):
        return self.__response_headers

    def HTTPContext(self):
        return HTTPGatewayContext(self)


class HTTPGatewayContext(object):
    def __init__(self, invoke_context: InvokeContext):
        self.__headers = hs.decap_headers(invoke_context.Headers())
        self.__invoke_context = invoke_context
        self.__response_headers = hs.GoLikeHeaders({})

    def RequestURL(self):
        return self.__invoke_context._request_url

    def Method(self):
        return self.__invoke_context._method

    def Headers(self):
        return self.__headers

    def SetResponseHeaders(self, headers, status_code, content_type=None):
        self.__response_headers = set_response_headers(
            self.GetResponseHeaders(), headers, status_code,
            content_type=content_type)

    def GetResponseHeaders(self):
        return self.__response_headers

    def Format(self):
        return self.__invoke_context.Format()


def context_from_format(format_def, **kwargs) -> (InvokeContext, object):
    app_id = os.environ.get(constants.FN_APP_ID)
    fn_id = os.environ.get(constants.FN_ID)

    if format_def == constants.HTTPSTREAM:
        data = kwargs.get("data")
        request = kwargs.get("request")

        method = request.headers.get(constants.FN_HTTP_METHOD)
        request_url = request.headers.get(
            constants.FN_HTTP_REQUEST_URL)
        deadline = request.headers.get(constants.FN_DEADLINE)
        call_id = request.headers.get(constants.FN_CALL_ID)
        content_type = request.content_type

        ctx = InvokeContext(
            app_id, fn_id, call_id,
            content_type=content_type,
            deadline=deadline,
            config=os.environ,
            headers=hs.GoLikeHeaders(dict(request.headers)),
            method=method,
            request_url=request_url,
            fn_format=constants.HTTPSTREAM,
        )

        return ctx, data
