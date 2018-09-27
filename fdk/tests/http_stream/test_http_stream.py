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

import asyncio
import pytest
import ujson

from fdk import constants
from fdk import http_stream
from xml.etree import ElementTree

from fdk.tests import funcs


async def setup_application_client(aiohttp_client, handle_func):
    app = http_stream.setup_unix_server(
        handle_func,
        loop=asyncio.get_event_loop()
    )

    return await aiohttp_client(app)


async def test_override_content_type(aiohttp_client):
    client = await setup_application_client(
        aiohttp_client, funcs.content_type)
    resp = await client.post("/call")
    resp_data = await resp.text()

    assert 200 == resp.status
    assert "OK" == resp_data
    assert "text/plain" in resp.content_type


async def test_parse_request_without_data(aiohttp_client):
    client = await setup_application_client(
        aiohttp_client, funcs.dummy_func)

    resp = await client.post("/call")
    resp_data = await resp.text()

    assert 200 == resp.status
    assert "Hello World" == ujson.loads(resp_data)
    assert "application/json" in resp.content_type


async def test_parse_request_with_data(aiohttp_client):
    client = await setup_application_client(
        aiohttp_client, funcs.dummy_func)
    resp = await client.post("/call", json={"name": "John"})
    resp_data = await resp.text()

    assert 200 == resp.status
    assert "Hello John" == ujson.loads(resp_data)
    assert "application/json" in resp.content_type


async def test_custom_response_object(aiohttp_client):
    client = await setup_application_client(
        aiohttp_client, funcs.custom_response)
    resp = await client.post(
        "/call", json={"name": "John"})

    assert 201 == resp.status


async def test_errored_func(aiohttp_client):
    client = await setup_application_client(
        aiohttp_client, funcs.expectioner)
    resp = await client.post("/call")

    assert 500 == resp.status
    assert "custom_error" in resp.reason


async def test_none_func(aiohttp_client):
    client = await setup_application_client(
        aiohttp_client, funcs.none_func)
    resp = await client.post("/call")

    assert 0 == resp.content_length
    assert 200 == resp.status


async def test_coro_func(aiohttp_client):
    client = await setup_application_client(
        aiohttp_client, funcs.coro)
    resp = await client.post("/call")

    assert 200 == resp.status
    assert 'hello from coro' == ujson.loads(await resp.text())


# async def test_deadline(aiohttp_client):
#     timeout = 5
#     client = await setup_application_client(
#         aiohttp_client, funcs.timed_sleepr(timeout + 1))

#
# async def test_default_deadline(aiohttp_client):
#     client = await setup_application_client(
#         aiohttp_client, funcs.coro)


async def test_valid_xml(aiohttp_client):
    client = await setup_application_client(
        aiohttp_client, funcs.valid_xml)
    resp = await client.post("/call")

    ElementTree.fromstring(await resp.text())

    assert "application/xml" in resp.content_type


async def test_invalid_xml(aiohttp_client):
    client = await setup_application_client(
        aiohttp_client, funcs.invalid_xml)
    resp = await client.post("/call")

    with pytest.raises(ElementTree.ParseError):
        ElementTree.fromstring(await resp.text())


async def test_access_decaped_headers(aiohttp_client):
    client = await setup_application_client(
        aiohttp_client, funcs.encaped_header)
    header_key = constants.FN_HTTP_PREFIX + "custom-header-maybe"
    value = "aloha"
    resp = await client.post("/call", headers={
        header_key: value
    })
    assert value == resp.headers.get(header_key)
