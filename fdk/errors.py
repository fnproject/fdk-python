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

import os
import uuid

from fdk import context
from fdk import headers
from fdk import response


class JSONDispatchException(Exception):

    def __init__(self, status, message):
        """
        JSON response with error
        :param status: HTTP status code
        :param message: error message
        """
        self.status = status
        self.message = message

    def response(self):
        resp_headers = headers.GoLikeHeaders({})
        resp_headers.set("content-type", "text/plain; charset=utf-8")
        return response.JSONResponse(
            None,
            response_data={
                "error": {
                    "message": self.message,
                }
            },
            headers=resp_headers,
            status_code=self.status
        )


class CloudEventDispatchException(Exception):

    def __init__(self, status, message):
        """
        JSON response with error
        :param status: HTTP status code
        :param message: error message
        """
        self.status = status
        self.message = message

    def response(self):
        resp_headers = headers.GoLikeHeaders({})
        resp_headers.set(
            "content-type",
            "application/json")
        app = os.environ.get("FN_APP_NAME")
        path = os.environ.get("FN_PATH")
        return response.CloudEventResponse(
            context.CloudEventContext(app, path, "", cloudevent={
                "cloudEventsVersion": "0.1",
                "eventID": uuid.uuid4().hex,
                "source": "fdk-python",
                "eventType": "fdk-python-error",
                "eventTypeVersion": "0.1",
                "schemaURL": "",
                "contentType": "application/json",
                "extensions": {
                    "protocol": {}
                },
            }),
            response_data={
                "error": {
                    "message": self.message,
                }
            },
            headers=resp_headers,
            status_code=self.status
        )


def error_class_from_format(format_def):
    if format_def == "json":
        return JSONDispatchException
    if format_def == "cloudevent":
        return CloudEventDispatchException
