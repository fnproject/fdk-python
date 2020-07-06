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
import json
import pytest

from fdk import constants
from fdk import event_handler
from fdk import fixtures

from fdk.tests import funcs


@pytest.mark.asyncio
async def test_override_content_type():
    call = await fixtures.setup_fn_call(
        funcs.content_type)
    content, status, headers = await call

    assert 200 == status
    assert "OK" == content
    assert headers.get("content-type") == "application/json"
    # we've had issues with 'Content-Type: None' slipping in
    assert headers.get("Content-Type") is None
    assert headers.get(
        constants.FN_FDK_VERSION) == constants.VERSION_HEADER_VALUE


@pytest.mark.asyncio
async def test_parse_request_without_data():
    call = await fixtures.setup_fn_call(funcs.dummy_func)

    content, status, headers = await call
    assert 200 == status
    assert "Hello World" == content


@pytest.mark.asyncio
async def test_parse_request_with_data():
    input_content = json.dumps(
        {"name": "John"}).encode("utf-8")
    call = await fixtures.setup_fn_call(
        funcs.dummy_func, content=input_content)
    content, status, headers = await call

    assert 200 == status
    assert "Hello John" == content


@pytest.mark.asyncio
async def test_custom_response_object():
    input_content = json.dumps(
        {"name": "John"}).encode("utf-8")
    call = await fixtures.setup_fn_call(
        funcs.custom_response, input_content)
    content, status, headers = await call

    assert 201 == status


@pytest.mark.asyncio
async def test_encap_headers_gw():
    call = await fixtures.setup_fn_call(
        funcs.encaped_header,
        headers={
            "custom-header-maybe": "yo",
            "content-type": "application/yo"
        },
        gateway=True,
    )
    content, status, headers = await call

    # make sure that content type is not encaped, and custom header is
    # when coming out of the fdk
    assert 200 == status
    assert "application/yo" in headers.get("content-type")
    assert "yo" in headers.get("fn-http-h-custom-header-maybe")


@pytest.mark.asyncio
async def test_encap_headers():
    call = await fixtures.setup_fn_call(
        funcs.encaped_header,
        headers={
            "custom-header-maybe": "yo",
            "content-type": "application/yo"
        }
    )
    content, status, headers = await call

    # make sure that custom header is not encaped out of fdk
    assert 200 == status
    assert "application/yo" in headers.get("content-type")
    assert "yo" in headers.get("custom-header-maybe")


@pytest.mark.asyncio
async def test_errored_func():
    call = await fixtures.setup_fn_call(funcs.expectioner)
    content, status, headers = await call

    assert 502 == status


@pytest.mark.asyncio
async def test_none_func():
    call = await fixtures.setup_fn_call(funcs.none_func)
    content, status, headers = await call

    assert 0 == len(content)
    assert 200 == status


@pytest.mark.asyncio
async def test_coro_func():
    call = await fixtures.setup_fn_call(funcs.coro)
    content, status, headers = await call

    assert 200 == status
    assert 'hello from coro' == content


@pytest.mark.asyncio
async def test_deadline():
    timeout = 5
    now = dt.datetime.now(dt.timezone.utc).astimezone()
    now += dt.timedelta(0, float(timeout))

    call = await fixtures.setup_fn_call(
        funcs.timed_sleepr(timeout + 1),
        deadline=now.isoformat())
    _, status, _ = await call

    assert 502 == status


@pytest.mark.asyncio
async def test_default_enforced_response_code():
    event_coro = event_handler.event_handle(
        fixtures.code(funcs.code404))

    http_resp = await event_coro(fixtures.fake_request(gateway=True))

    assert http_resp.status == 200
    assert http_resp.headers.get(constants.FN_HTTP_STATUS) == "404"


@pytest.mark.asyncio
async def test_enforced_response_codes_502():
    event_coro = event_handler.event_handle(
        fixtures.code(funcs.code502))

    http_resp = await event_coro(fixtures.fake_request(gateway=True))

    assert http_resp.status == 502
    assert http_resp.headers.get(constants.FN_HTTP_STATUS) == "502"


@pytest.mark.asyncio
async def test_enforced_response_codes_504():
    event_coro = event_handler.event_handle(
        fixtures.code(funcs.code504))

    http_resp = await event_coro(fixtures.fake_request(gateway=True))

    assert http_resp.status == 504
    assert http_resp.headers.get(constants.FN_HTTP_STATUS) == "504"


def test_log_frame_header(monkeypatch, capsys):
    monkeypatch.setattr("fdk.event_handler.fn_logframe_name", "foo")
    monkeypatch.setattr("fdk.event_handler.fn_logframe_hdr", "Fn-Call-Id")
    headers = {"fn-call-id": 12345}

    event_handler.log_frame_header(headers)

    captured = capsys.readouterr()
    assert "\nfoo=12345\n" in captured.out
    assert "\nfoo=12345\n" in captured.err


@pytest.mark.asyncio
async def test_request_url_and_method_set_with_gateway():
    headers = {
        "fn-http-method": "PUT",
        "fn-http-request-url": "/foo-bar?baz",
        "fn-http-h-not-aheader": "nothttp"
    }

    funcs.setup_context_capture()

    call = await fixtures.setup_fn_call_raw(
        funcs.capture_request_ctx,
        headers=headers
    )
    content, status, headers = await call
    assert content == "OK"

    ctx = funcs.get_captured_context()

    assert ctx.RequestURL() == "/foo-bar?baz", "request URL mismatch, got %s" \
                                               % ctx.RequestURL()
    assert ctx.Method() == "PUT", "method mismatch got %s" % ctx.Method()
    assert "fn-http-h-not-aheader" in ctx.Headers()
    assert ctx.Headers()["fn-http-h-not-aheader"] == "nothttp"


@pytest.mark.asyncio
async def test_encap_request_headers_gateway():
    headers = {
        "fn-intent": "httprequest",
        "fn-http-h-my-header": "foo",
        "fn-http-h-funny-header": ["baz", "bob"],
        "funny-header": "not-this-one",
    }

    funcs.setup_context_capture()
    call = await fixtures.setup_fn_call_raw(
        funcs.capture_request_ctx,
        content=None,
        headers=headers
    )

    content, status, headers = await call

    assert content == 'OK'

    input_ctx = funcs.get_captured_context()

    headers = input_ctx.Headers()

    assert "my-header" in headers
    assert "funny-header" in headers

    assert headers["my-header"] == "foo"
    assert headers["funny-header"] == ["baz", "bob"]

    assert input_ctx.HTTPHeaders() == {"my-header": "foo",
                                       "funny-header": ["baz", "bob"]}


@pytest.mark.asyncio
async def test_bytes_response():
    call = await fixtures.setup_fn_call(funcs.binary_result)
    content, status, headers = await call
    assert content == bytes([1, 2, 3, 4, 5])
