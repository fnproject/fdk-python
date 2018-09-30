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
from fdk import headers


class RequestContext(object):

    def __init__(self, app_id, fn_id, call_id,
                 fn_format, content_type="text/plain", deadline=None,
                 config=None, headers=None, arguments=None,
                 request_url=None, method="POST"):
        """
        Request context here to be a placeholder
        for request-specific attributes
        """
        self.__app_id = app_id
        self.__fn_id = fn_id
        self.__call_id = call_id
        self.__config = config if config else {}
        self.__headers = headers if headers else {}
        self.__arguments = {} if not arguments else arguments
        self.__fn_format = fn_format
        self.__deadline = deadline
        self.__content_type = content_type
        self.__request_url = request_url
        self.__method = method

    def AppID(self):
        return self.__app_id

    def FnID(self):
        return self.__fn_id

    # def Route(self):
    #     return self.__app_route

    def CallID(self):
        return self.__call_id

    def Config(self):
        return self.__config

    def Headers(self):
        return self.__headers

    def Arguments(self):
        return self.__arguments

    def Format(self):
        return self.__fn_format

    def Deadline(self):
        if self.__deadline is None:
            now = dt.datetime.now(dt.timezone.utc).astimezone()
            now += dt.timedelta(0, float(constants.DEFAULT_DEADLINE))
            return now.isoformat()
        return self.__deadline

    def RequestContentType(self):
        return self.__content_type

    def RequestURL(self):
        return self.__request_url

    def Method(self):
        return self.__method


class HTTPStreamContext(RequestContext):
    def __init__(self, app_id, fn_id, call_id,
                 content_type="application/octet-stream",
                 deadline=None,
                 config=None,
                 headers=None,
                 request_url=None,
                 method=None):
        super(HTTPStreamContext, self).__init__(
            app_id, fn_id, call_id, constants.HTTPSTREAM,
            deadline=deadline,
            config=config,
            headers=headers,
            content_type=content_type,
            request_url=request_url,
            method=method,
        )


def decap_headers(request_response):
    ctx_headers = headers.GoLikeHeaders({})
    for k, v in dict(request_response.headers).items():
        if k.startswith(constants.FN_HTTP_PREFIX):
            ctx_headers.set(k.lstrip(constants.FN_HTTP_PREFIX), v)
        else:
            ctx_headers.set(k, v)
    return ctx_headers


def context_from_format(format_def, **kwargs) -> (RequestContext, object):
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

        ctx = HTTPStreamContext(
            app_id, fn_id, call_id,
            content_type=content_type,
            deadline=deadline,
            config=os.environ,
            headers=decap_headers(request),
            method=method,
            request_url=request_url
        )

        return ctx, data
