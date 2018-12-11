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
import datetime as dt
import h11
import json
import io
import pytest
import os

from fdk import constants
from fdk import fixtures
from fdk.http import routine

from fdk.tests import funcs


@pytest.mark.asyncio
async def test_override_content_type():
    call = await fixtures.setup_fn_call(
        funcs.content_type)
    content, status, headers = await call

    assert 200 == status
    assert "OK" == content
    assert "text/plain" in headers.get("Content-Type")


@pytest.mark.asyncio
async def test_parse_request_without_data():
    call = await fixtures.setup_fn_call(funcs.dummy_func)

    content, status, headers = await call
    print(headers)
    assert 200 == status
    assert "Hello World" == content
    assert "text/plain" in headers.get("Content-Type")


@pytest.mark.asyncio
async def test_parse_request_with_data():
    input_content = json.dumps(
        {"name": "John"}).encode("utf-8")
    call = await fixtures.setup_fn_call(
        funcs.dummy_func, content=input_content)
    content, status, headers = await call

    assert 200 == status
    assert "Hello John" == content
    assert "text/plain" in headers.get("Content-Type")


@pytest.mark.asyncio
async def test_custom_response_object():
    input_content = json.dumps(
        {"name": "John"}).encode("utf-8")
    call = await fixtures.setup_fn_call(
        funcs.custom_response, input_content)
    content, status, headers = await call

    assert 201 == status


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
async def test_io_limit_exceeded():
    con = h11.Connection(h11.CLIENT)
    data = os.urandom(5 * constants.IO_LIMIT)
    headers = {
        'host': 'localhost:5000',
        'user-agent': 'curl/7.54.0',
        'accept': '*/*',
        'content-length': str(len(data)),
        'content-type': 'application/x-www-form-urlencoded',
        'expect': '100-continue',
        'connection': 'keep-alive',
    }

    stream = asyncio.StreamReader(
        loop=asyncio.get_event_loop())
    stream.feed_data(
        con.send(
            h11.Request(
                method="POST",
                target="/call",
                headers=headers.items()
            )
        )
    )
    d = con.send(h11.Data(data=data))
    print(len(d))
    stream.feed_data(d)
    stream.feed_data(con.send(h11.EndOfMessage()))
    stream.feed_eof()
    rq, rq_data = await routine.read_request(
        h11.Connection(h11.SERVER), stream)

    assert rq is not None
    assert rq_data is not None
    assert rq_data.seek(0, io.SEEK_END) == len(data)


@pytest.mark.asyncio
async def test_connection_closed():
    stream = asyncio.StreamReader(loop=asyncio.get_event_loop())
    stream.feed_eof()
    try:
        await routine.read_request(
            h11.Connection(h11.SERVER), stream)
    except Exception as ex:
        assert "connection closed" in str(ex)
