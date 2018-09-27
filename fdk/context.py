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
import sys

from fdk import constants
from fdk import headers
from fdk import response
from fdk import parser


class JSONDispatchException(Exception):

    def __init__(self, context, status, message):
        """
        JSON response with error
        :param status: HTTP status code
        :param message: error message
        """
        self.status = status
        self.message = message
        self.context = context

    def response(self):
        resp_headers = headers.GoLikeHeaders({})
        resp_headers.set("content-type", "text/plain; charset=utf-8")
        return response.RawResponse(
            self.context,
            response_data={
                "error": {
                    "message": self.message,
                }
            },
            headers=resp_headers,
            status_code=self.status)


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
        # self.__app_route = route
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


class JSONContext(RequestContext):

    def __init__(self, app_name, route, call_id,
                 content_type="text/plain",
                 deadline=None,
                 config=None,
                 headers=None,
                 request_url=None):
        super(JSONContext, self).__init__(
            app_name, route, call_id, constants.JSON,
            deadline=deadline,
            config=config,
            headers=headers,
            content_type=content_type,
            request_url=request_url,
        )


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
        )


class CloudEventContext(RequestContext):

    def __init__(self, app_id, fn_id, call_id,
                 content_type="application/cloudevents+json",
                 deadline=None,
                 config=None,
                 headers=None,
                 request_url=None,
                 cloudevent=None):
        super(CloudEventContext, self).__init__(
            app_id, fn_id, call_id, constants.CLOUDEVENT,
            deadline=deadline,
            config=config,
            headers=headers,
            content_type=content_type,
            request_url=request_url,
        )
        self.cloudevent = cloudevent if cloudevent else {}


def decap_headers(request):
    ctx_headers = headers.GoLikeHeaders({})

    for k, v in dict(request.headers).items():
        if constants.FN_HTTP_PREFIX in k:
            ctx_headers.set(k.lstrip(constants.FN_HTTP_PREFIX), v)

    return ctx_headers


def context_from_format(
        format_def, stream, **kwargs) -> (RequestContext, object):
    app_id = os.environ.get("FN_APP_ID")
    fn_id = os.environ.get("FN_FN_ID")

    if format_def == constants.HTTPSTREAM:
        data = kwargs.get("data")
        request = kwargs.get("request")

        method = request.headers.get("Fn-Http-Method")
        request_url = request.headers.get("Fn-Http-Request-Url")
        deadline = request.headers.get("Fn-Deadline")
        call_id = request.headers.get("Fn-Call-Id")
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

    if format_def == constants.CLOUDEVENT:
        incoming_request = parser.read_json(stream)
        call_id = incoming_request.get("eventID")
        content_type = incoming_request.get("contentType")
        extensions = incoming_request.get("extensions")
        deadline = extensions.get("deadline")
        protocol = extensions.get("protocol")
        json_headers = headers.GoLikeHeaders(protocol.get("headers"))
        data = incoming_request.get("data")
        if "data" in incoming_request:
            del incoming_request["data"]

        ctx = CloudEventContext(
            app_id, fn_id, call_id,
            content_type=content_type,
            deadline=deadline,
            config=os.environ,
            headers=json_headers,
            request_url=protocol.get("request_url"),
            cloudevent=incoming_request,
        )
        return ctx, data

    if format_def == constants.JSON:
        incoming_request = parser.read_json(stream)
        call_id = incoming_request.get("call_id")

        content_type = incoming_request.get("content_type")
        protocol = incoming_request.get("protocol")

        json_headers = headers.GoLikeHeaders(protocol.get("headers"))

        ctx = JSONContext(
            app_id, fn_id, call_id,
            content_type=content_type,
            deadline=incoming_request.get("deadline"),
            config=os.environ, headers=json_headers,
            request_url=protocol.get("request_url")
        )
        return ctx, incoming_request.get("body", "{}")

    if format_def not in [constants.CLOUDEVENT,
                          constants.JSON,
                          constants.HTTPSTREAM]:
        print("incompatible function format!", file=sys.stderr, flush=True)
        sys.exit("incompatible function format!")
