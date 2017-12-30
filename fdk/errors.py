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

from fdk import headers
from fdk import response


class HTTPDispatchException(Exception):

    def __init__(self, context, status, message):
        """
        HTTP response with error
        :param status: HTTP status code
        :param message: error message
        """
        self.status = status
        self.message = message
        self.context = context

    def response(self):
        return response.RawResponse(
            self.context,
            status_code=self.status,
            headers={
                "content-type": "text/plain"
            },
            response_data=self.message)


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
