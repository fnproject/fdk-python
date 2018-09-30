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
import pytest
import ujson

from xml.etree import ElementTree

from fdk import fixtures
from fdk.tests import funcs


async def test_override_content_type(aiohttp_client):
    call = await fixtures.setup_fn_call(
        aiohttp_client, funcs.content_type)
    content, status, headers = await call

    assert 200 == status
    assert "OK" == content.decode("utf8")
    assert "text/plain" in headers.get("Content-Type")


async def test_parse_request_without_data(aiohttp_client):
    call = await fixtures.setup_fn_call(
        aiohttp_client, funcs.dummy_func)

    content, status, headers = await call

    assert 200 == status
    assert "Hello World" == ujson.loads(content)
    assert "application/json" in headers.get("Content-Type")


async def test_parse_request_with_data(aiohttp_client):
    call = await fixtures.setup_fn_call(
        aiohttp_client, funcs.dummy_func, json={"name": "John"})
    content, status, headers = await call

    assert 200 == status
    assert "Hello John" == ujson.loads(content)
    assert "application/json" in headers.get("Content-Type")


async def test_custom_response_object(aiohttp_client):
    call = await fixtures.setup_fn_call(
        aiohttp_client, funcs.custom_response, json={"name": "John"})
    content, status, headers = await call

    assert 201 == status


async def test_errored_func(aiohttp_client):
    call = await fixtures.setup_fn_call(
        aiohttp_client, funcs.expectioner)
    content, status, headers = await call

    assert 500 == status


async def test_none_func(aiohttp_client):
    call = await fixtures.setup_fn_call(
        aiohttp_client, funcs.none_func)
    content, status, headers = await call

    assert 0 == len(content)
    assert 200 == status


async def test_coro_func(aiohttp_client):
    call = await fixtures.setup_fn_call(
        aiohttp_client, funcs.coro)
    content, status, headers = await call

    assert 200 == status
    assert 'hello from coro' == ujson.loads(content)


async def test_deadline(aiohttp_client):
    timeout = 5
    now = dt.datetime.now(dt.timezone.utc).astimezone()
    now += dt.timedelta(0, float(timeout))

    call = await fixtures.setup_fn_call(
        aiohttp_client, funcs.timed_sleepr(timeout + 1),
        deadline=now.isoformat())
    _, status, _ = await call

    assert 502 == status


async def test_default_deadline(aiohttp_client):
    timeout = 5

    call = await fixtures.setup_fn_call(
        aiohttp_client, funcs.timed_sleepr(timeout))
    _, status, _ = await call

    assert 200 == status


async def test_valid_xml(aiohttp_client):
    call = await fixtures.setup_fn_call(
        aiohttp_client, funcs.valid_xml)
    content, status, headers = await call

    ElementTree.fromstring(content)

    assert "application/xml" in headers.get("Content-Type")


async def test_invalid_xml(aiohttp_client):
    call = await fixtures.setup_fn_call(
        aiohttp_client, funcs.invalid_xml)
    content, status, headers = await call

    with pytest.raises(ElementTree.ParseError):
        ElementTree.fromstring(content)


async def test_access_decaped_headers(aiohttp_client):
    header_key = "custom-header-maybe"
    value = "aloha"

    call = await fixtures.setup_fn_call(
        aiohttp_client, funcs.encaped_header, headers={
            header_key: value
        }
    )
    content, status, headers = await call
    assert value == headers.get(header_key)


async def test_access_method_request_url(aiohttp_client):
    header_key = "Response-Request-URL"
    value = "/hello/can-you-hear-me"
    method = "PUT"

    call = await fixtures.setup_fn_call(
        aiohttp_client, funcs.access_request_url,
        request_url=value, method=method,
    )
    _, _, headers = await call

    assert header_key in headers
    assert value == headers.get(header_key)
