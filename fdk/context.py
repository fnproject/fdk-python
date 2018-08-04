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

from fdk import headers
from fdk import response
from fdk import parser


DEFAULT_DEADLINE = 30


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

    def __init__(self, app_name, route, call_id,
                 fn_format, content_type="text/plain",
                 execution_type=None, deadline=None,
                 config=None, headers=None, arguments=None,
                 request_url=None):
        """
        Request context here to be a placeholder
        for request-specific attributes
        """
        self.__app_name = app_name
        self.__app_route = route
        self.__call_id = call_id
        self.__config = config if config else {}
        self.__headers = headers if headers else {}
        self.__arguments = {} if not arguments else arguments
        self.__fn_format = fn_format
        self.__exec_type = execution_type
        self.__deadline = deadline
        self.__content_type = content_type
        self.__request_url = request_url

    def AppName(self):
        return self.__app_name

    def Route(self):
        return self.__app_route

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
            now += dt.timedelta(0, float(DEFAULT_DEADLINE))
            return now.isoformat()
        return self.__deadline

    def ExecutionType(self):
        return self.__exec_type

    def RequestContentType(self):
        return self.__content_type

    def RequestURL(self):
        return self.__request_url


class JSONContext(RequestContext):

    def __init__(self, app_name, route, call_id,
                 content_type="text/plain",
                 deadline=None,
                 execution_type=None,
                 config=None,
                 headers=None,
                 request_url=None):
        super(JSONContext, self).__init__(
            app_name, route, call_id, "json",
            execution_type=execution_type,
            deadline=deadline,
            config=config,
            headers=headers,
            content_type=content_type,
            request_url=request_url,
        )


class CloudEventContext(RequestContext):

    def __init__(self, app_name, route, call_id,
                 content_type="application/cloudevents+json",
                 deadline=None,
                 execution_type=None,
                 config=None,
                 headers=None,
                 request_url=None,
                 cloudevent=None):
        super(CloudEventContext, self).__init__(
            app_name, route, call_id, "cloudevent",
            execution_type=execution_type,
            deadline=deadline,
            config=config,
            headers=headers,
            content_type=content_type,
            request_url=request_url,
        )
        self.cloudevent = cloudevent if cloudevent else {}


def context_from_format(format_def, stream) -> (RequestContext, object):
    app = os.environ.get("FN_APP_NAME")
    path = os.environ.get("FN_PATH")

    if format_def == "cloudevent":
        incoming_request = parser.read_json(stream)
        call_id = incoming_request.get("eventID")
        content_type = incoming_request.get("contentType")
        extensions = incoming_request.get("extensions")
        deadline = extensions.get("deadline")
        protocol = extensions.get("protocol", {
            "headers": {},
            "type": "http",
            "method": "GET",
            "request_url": "http://localhost:8080/r/{0}{1}".format(app, path),
        })
        json_headers = headers.GoLikeHeaders(protocol.get("headers"))
        data = incoming_request.get("data")
        if "data" in incoming_request:
            del incoming_request["data"]

        ctx = CloudEventContext(
            app, path, call_id,
            content_type=content_type,
            execution_type=os.getenv("FN_TYPE"),
            deadline=deadline,
            config=os.environ,
            headers=json_headers,
            request_url=protocol.get("request_url"),
            cloudevent=incoming_request,
        )
        return ctx, data

    if format_def == "json":
        incoming_request = parser.read_json(stream)
        call_id = incoming_request.get("call_id")

        content_type = incoming_request.get("content_type")
        protocol = incoming_request.get("protocol", {
            "headers": {},
            "type": "http",
            "method": "GET",
            "request_url": "http://localhost:8080/r/{0}{1}".format(app, path),
        })

        json_headers = headers.GoLikeHeaders(protocol.get("headers"))
        call_type = json_headers.get("fn-type", "sync")

        ctx = JSONContext(
            app, path, call_id,
            content_type=content_type,
            execution_type=call_type,
            deadline=incoming_request.get("deadline"),
            config=os.environ, headers=json_headers,
            request_url=protocol.get("request_url")
        )
        return ctx, incoming_request.get("body", "{}")

    if format_def not in ["cloudevent", "json"]:
        print("incompatible function format!", file=sys.stderr, flush=True)
        sys.exit("incompatible function format!")
