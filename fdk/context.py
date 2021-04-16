#
# Copyright (c) 2019, 2020 Oracle and/or its affiliates. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import datetime as dt
import io
import os
import random
from fdk import constants
from fdk import headers as hs
from fdk import log
from collections import namedtuple


class InvokeContext(object):

    def __init__(self, app_id, app_name, fn_id, fn_name, call_id,
                 content_type="application/octet-stream",
                 deadline=None, config=None,
                 headers=None, request_url=None,
                 method="POST", fn_format=None,
                 tracing_context=None):
        """
        Request context here to be a placeholder
        for request-specific attributes
        :param app_id: Fn App ID
        :type app_id: str
        :param app_name: Fn App name
        :type app_name: str
        :param fn_id: Fn App Fn ID
        :type fn_id: str
        :param fn_name: Fn name
        :type fn_name: str
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
        :param tracing_context: tracing context
        :type tracing_context: TracingContext
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
        self.__app_name = app_name
        self.__fn_name = fn_name
        self.__tracing_context = tracing_context if tracing_context else None

        log.log("request headers. gateway: {0} {1}"
                .format(self.__is_gateway(), headers))

        if self.__is_gateway():
            self.__headers = hs.decap_headers(headers, True)
            self.__http_headers = hs.decap_headers(headers, False)

    def AppID(self):
        return self.__app_id

    def AppName(self):
        return self.__app_name

    def FnID(self):
        return self.__fn_id

    def FnName(self):
        return self.__fn_name

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

    def TracingContext(self):
        return self.__tracing_context

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


class TracingContext(object):

    def __init__(self, is_tracing_enabled, trace_collector_url,
                 trace_id, span_id, parent_span_id,
                 is_sampled, flags):
        """
        Tracing context here to be a placeholder
        for tracing-specific attributes
        :param is_tracing_enabled: tracing enabled flag
        :type is_tracing_enabled: bool
        :param trace_collector_url: APM Trace Collector Endpoint URL
        :type trace_collector_url: str
        :param trace_id: Trace ID
        :type trace_id: str
        :param span_id: Span ID
        :type span_id: str
        :param parent_span_id: Parent Span ID
        :type parent_span_id: str
        :param is_sampled: Boolean for emmitting spans
        :type is_sampled: int (0 or 1)
        :param flags: Debug flags
        :type flags: int (0 or 1)
        """
        self.__is_tracing_enabled = is_tracing_enabled
        self.__trace_collector_url = trace_collector_url
        self.__trace_id = trace_id
        self.__span_id = span_id
        self.__parent_span_id = parent_span_id
        self.__is_sampled = is_sampled
        self.__flags = flags
        self.__app_name = os.environ.get(constants.FN_APP_NAME)
        self.__app_id = os.environ.get(constants.FN_APP_ID)
        self.__fn_name = os.environ.get(constants.FN_NAME)
        self.__fn_id = os.environ.get(constants.FN_ID)

    def is_tracing_enabled(self):
        return self.__is_tracing_enabled

    def trace_collector_url(self):
        return self.__trace_collector_url

    def trace_id(self):
        return self.__trace_id

    def span_id(self):
        return self.__span_id

    def parent_span_id(self):
        return self.__parent_span_id

    def is_sampled(self):
        return bool(self.__is_sampled)

    def flags(self):
        return self.__flags

    # this is a helper method specific for py_zipkin
    def zipkin_attrs(self):
        ZipkinAttrs = namedtuple(
            "ZipkinAttrs",
            "trace_id, span_id, parent_span_id, is_sampled, flags"
        )

        trace_id = self.__trace_id
        span_id = self.__span_id
        parent_span_id = self.__parent_span_id
        is_sampled = bool(self.__is_sampled)
        trace_flags = self.__flags

        # As the fnLb sends the parent_span_id as the span_id
        # assign the parent span id as the span id.
        if parent_span_id is None and span_id is not None:
            parent_span_id = span_id
            span_id = generate_id()

        zipkin_attrs = ZipkinAttrs(
            trace_id,
            span_id,
            parent_span_id,
            is_sampled,
            trace_flags
        )
        return zipkin_attrs

    def service_name(self, override=None):
        # in case of missing app and function name env variables
        service_name = (
            override
            if override is not None
            else str(self.__app_name) + "::" + str(self.__fn_name)
        )
        return service_name.lower()

    def annotations(self):
        annotations = {
            "generatedBy": "faas",
            "appName": self.__app_name,
            "appID": self.__app_id,
            "fnName": self.__fn_name,
            "fnID": self.__fn_id,
        }
        return annotations


def generate_id():
    return "{:016x}".format(random.getrandbits(64))


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
    app_name = os.environ.get(constants.FN_APP_NAME)
    fn_name = os.environ.get(constants.FN_NAME)
    # the tracing enabled env variable is passed as a "0" or "1" string
    # and therefore needs to be converted appropriately.
    is_tracing_enabled = os.environ.get(constants.OCI_TRACING_ENABLED)
    is_tracing_enabled = (
        bool(int(is_tracing_enabled))
        if is_tracing_enabled is not None
        else False
    )
    trace_collector_url = os.environ.get(constants.OCI_TRACE_COLLECTOR_URL)

    if format_def == constants.HTTPSTREAM:
        data = kwargs.get("data")
        headers = kwargs.get("headers")

        # zipkin tracing http headers
        trace_id = span_id = parent_span_id = is_sampled = trace_flags = None
        tracing_context = None
        if is_tracing_enabled:
            # we generate the trace_id if tracing is enabled
            # but the traceId zipkin header is missing.
            trace_id = headers.get(constants.X_B3_TRACEID)
            trace_id = generate_id() if trace_id is None else trace_id

            span_id = headers.get(constants.X_B3_SPANID)
            parent_span_id = headers.get(constants.X_B3_PARENTSPANID)

            # span_id is also generated if the zipkin header is missing.
            span_id = generate_id() if span_id is None else span_id

            # is_sampled should be a boolean in the form of a "0/1" but
            # legacy samples have them as "False/True"
            is_sampled = headers.get(constants.X_B3_SAMPLED)
            is_sampled = int(is_sampled) if is_sampled is not None else 1

            # not currently used but is defined by the zipkin headers standard
            trace_flags = headers.get(constants.X_B3_FLAGS)

        # tracing context will be an empty object
        # if tracing is not enabled or the flag is missing.
        # this prevents the customer code from failing if they decide to
        # disable tracing. An empty tracing context will not
        # emit spans due to is_sampled being None.
        tracing_context = TracingContext(
            is_tracing_enabled,
            trace_collector_url,
            trace_id,
            span_id,
            parent_span_id,
            is_sampled,
            trace_flags
        )

        method = headers.get(constants.FN_HTTP_METHOD)
        request_url = headers.get(constants.FN_HTTP_REQUEST_URL)
        deadline = headers.get(constants.FN_DEADLINE)
        call_id = headers.get(constants.FN_CALL_ID)
        content_type = headers.get(constants.CONTENT_TYPE)

        ctx = InvokeContext(
            app_id, app_name, fn_id, fn_name, call_id,
            content_type=content_type,
            deadline=deadline,
            config=os.environ,
            headers=headers,
            method=method,
            request_url=request_url,
            fn_format=constants.HTTPSTREAM,
            tracing_context=tracing_context,
        )

        return ctx, data
