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
import io
import os

from fdk import constants
from fdk import headers as hs
from fdk import log


class InvokeContext(object):

    def __init__(self, app_id, fn_id, call_id,
                 content_type="application/octet-stream",
                 deadline=None, config=None,
                 headers=None, request_url=None,
                 method="POST", fn_format=None):
        """
        Request context here to be a placeholder
        for request-specific attributes
        :param app_id: Fn App ID
        :type app_id: str
        :param fn_id: Fn App Fn ID
        :type fn_id: str
        :param call_id: Fn call ID
        :type call_id: str
        :param content_type: request content type
        :type content_type: str
        :param deadline: request deadline
        :type deadline: str
        :param config: an app/fn config
        :type config: dict
        :param headers: request headers
        :type headers: dict
        :param request_url: request URL
        :type request_url: str
        :param method: request method
        :type method: str
        :param fn_format: function format
        :type fn_format: str
        """
        self.__app_id = app_id
        self.__fn_id = fn_id
        self.__call_id = call_id
        self.__config = config if config else {}
        self.__headers = headers if headers else {}
        self.__http_headers = {}
        self.__deadline = deadline
        self.__content_type = content_type
        self._request_url = request_url
        self._method = method
        self.__response_headers = {}
        self.__fn_format = fn_format

        log.log("request headers. gateway: {0} {1}"
                .format(self.__is_gateway(), headers))

        if self.__is_gateway():
            self.__headers = hs.decap_headers(headers, True)
            self.__http_headers = hs.decap_headers(headers, False)

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

    def HTTPHeaders(self):
        return self.__http_headers

    def Format(self):
        return self.__fn_format

    def Deadline(self):
        if self.__deadline is None:
            now = dt.datetime.now(dt.timezone.utc).astimezone()
            now += dt.timedelta(0, float(constants.DEFAULT_DEADLINE))
            return now.isoformat()
        return self.__deadline

    def SetResponseHeaders(self, headers, status_code):
        log.log("setting headers. gateway: {0}".format(self.__is_gateway()))
        if self.__is_gateway():
            headers = hs.encap_headers(headers, status=status_code)

        for k, v in headers.items():
            self.__response_headers[k.lower()] = v

    def GetResponseHeaders(self):
        return self.__response_headers

    def RequestURL(self):
        return self._request_url

    def Method(self):
        return self._method

    def __is_gateway(self):
        return (constants.FN_INTENT in self.__headers
                and self.__headers.get(constants.FN_INTENT)
                == constants.INTENT_HTTP_REQUEST)


def context_from_format(format_def: str, **kwargs) -> (
        InvokeContext, io.BytesIO):
    """
    Creates a context from request
    :param format_def: function format
    :type format_def: str
    :param kwargs: request-specific map of parameters
    :return: invoke context and data
    :rtype: tuple
    """

    app_id = os.environ.get(constants.FN_APP_ID)
    fn_id = os.environ.get(constants.FN_ID)

    if format_def == constants.HTTPSTREAM:
        data = kwargs.get("data")
        headers = kwargs.get("headers")

        method = headers.get(constants.FN_HTTP_METHOD)
        request_url = headers.get(
            constants.FN_HTTP_REQUEST_URL)
        deadline = headers.get(constants.FN_DEADLINE)
        call_id = headers.get(constants.FN_CALL_ID)
        content_type = headers.get(constants.CONTENT_TYPE)

        ctx = InvokeContext(
            app_id, fn_id, call_id,
            content_type=content_type,
            deadline=deadline,
            config=os.environ,
            headers=headers,
            method=method,
            request_url=request_url,
            fn_format=constants.HTTPSTREAM,
        )

        return ctx, data
