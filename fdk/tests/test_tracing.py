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

import os

from fdk import constants
from fdk.context import TracingContext
from fdk.context import InvokeContext
from fdk.context import context_from_format

app_id = "some_app_id"
app_name = "mock_app"
fn_id = "some_fn_id"
fn_name = "mock_fn"

is_tracing_enabled = True
trace_collector_url = "some_url_endpoint"
trace_id = "some_trace_id"
span_id = "some_span_id"
parent_span_id = "some_parent_span_id"
is_sampled = 1
trace_flags = 0

headers = {
    'host': 'localhost',
    'user-agent': 'curl/7.64.1',
    'content-length': '0',
    'accept': '*/*',
    'content-type': 'application/json',
    'fn-call-id': '01EY6NW519NG8G00GZJ000001Z',
    'fn-deadline': '2021-02-10T19:15:19Z',
    'accept-encoding': 'gzip',
    'x-b3-traceid': trace_id,
    'x-b3-spanid': span_id,
    'x-b3-parentspanid': parent_span_id,
    'x-b3-sampled': is_sampled,
    'x-b3-flags': trace_flags
}
call_id = headers.get(constants.FN_CALL_ID)
content_type = headers.get(constants.CONTENT_TYPE)
deadline = headers.get(constants.FN_DEADLINE)
method = headers.get(constants.FN_HTTP_METHOD)
request_url = headers.get(constants.FN_HTTP_REQUEST_URL)


def tracing_context():
    return TracingContext(
        is_tracing_enabled,
        trace_collector_url,
        trace_id,
        span_id,
        parent_span_id,
        is_sampled,
        trace_flags
    )


def invoke_context():
    return InvokeContext(
        app_id, app_name, fn_id, fn_name, call_id,
        content_type=content_type,
        deadline=deadline,
        config=os.environ,
        headers=headers,
        method=method,
        request_url=request_url,
        fn_format=constants.HTTPSTREAM,
        tracing_context=tracing_context(),
    )


def test_context_from_format_returns_correct_objects_when_tracing_enabled():
    os.environ[constants.FN_APP_ID] = app_id
    os.environ[constants.FN_ID] = fn_id
    os.environ[constants.FN_APP_NAME] = app_name
    os.environ[constants.FN_NAME] = fn_name
    os.environ[constants.OCI_TRACE_COLLECTOR_URL] = trace_collector_url
    os.environ[constants.OCI_TRACING_ENABLED] = "1"

    mock_invoke_context = invoke_context()
    mock_data = "some_data"

    actual_invoke_context, data = context_from_format(
        constants.HTTPSTREAM,
        headers=headers,
        data=mock_data
    )

    actual_tracing_context = actual_invoke_context.TracingContext().__dict__
    expected_tracing_context = mock_invoke_context.TracingContext().__dict__
    assert actual_tracing_context == expected_tracing_context
    assert data == mock_data

    os.environ.pop(constants.FN_APP_ID)
    os.environ.pop(constants.FN_ID)
    os.environ.pop(constants.FN_APP_NAME)
    os.environ.pop(constants.FN_NAME)
    os.environ.pop(constants.OCI_TRACE_COLLECTOR_URL)
    os.environ.pop(constants.OCI_TRACING_ENABLED)


def test_context_from_format_returns_correct_objects_when_tracing_disabled():
    os.environ[constants.FN_APP_ID] = app_id
    os.environ[constants.FN_ID] = fn_id
    os.environ[constants.FN_APP_NAME] = app_name
    os.environ[constants.FN_NAME] = fn_name
    os.environ[constants.OCI_TRACING_ENABLED] = "0"

    empty_tracing_context = TracingContext(
        False, None, None, None, None, None, None
    )
    mock_data = "some_data"

    actual_invoke_context, data = context_from_format(
        constants.HTTPSTREAM,
        headers=headers,
        data=mock_data
    )

    actual_tracing_context = actual_invoke_context.TracingContext().__dict__
    assert actual_tracing_context == empty_tracing_context.__dict__
    assert data == mock_data

    os.environ.pop(constants.FN_APP_ID)
    os.environ.pop(constants.FN_ID)
    os.environ.pop(constants.FN_APP_NAME)
    os.environ.pop(constants.FN_NAME)
    os.environ.pop(constants.OCI_TRACING_ENABLED)


def test_zipkin_attrs():
    mock_tracing_context = tracing_context()
    zipkin_attrs = mock_tracing_context.zipkin_attrs()

    assert zipkin_attrs.trace_id == trace_id
    assert zipkin_attrs.span_id == span_id
    assert zipkin_attrs.parent_span_id == parent_span_id
    assert zipkin_attrs.is_sampled is True
    assert zipkin_attrs.flags == 0


def test_tracing_context():
    os.environ[constants.FN_APP_NAME] = app_name
    os.environ[constants.FN_NAME] = fn_name
    mock_tracing_context = tracing_context()

    assert mock_tracing_context.trace_collector_url() == trace_collector_url
    assert mock_tracing_context.trace_id() == trace_id
    assert mock_tracing_context.span_id() == span_id
    assert mock_tracing_context.parent_span_id() == parent_span_id
    assert mock_tracing_context.is_sampled() == bool(is_sampled)
    assert mock_tracing_context.flags() == trace_flags
    assert mock_tracing_context.service_name() == "mock_app::mock_fn"

    os.environ.pop(constants.FN_APP_NAME)
    os.environ.pop(constants.FN_NAME)
