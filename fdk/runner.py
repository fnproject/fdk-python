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

import sys
import ujson
import os
import traceback
import signal
import datetime as dt
import iso8601
import types

from fdk import context
from fdk import errors
from fdk import headers
from fdk import response


async def with_deadline(ctx, handle_func, data):

    def timeout_func(*_):
        raise TimeoutError("function timed out")

    now = dt.datetime.now(dt.timezone.utc).astimezone()
    # ctx.Deadline() would never be an empty value,
    # by default it will be 30 secs from now
    deadline = ctx.Deadline()
    alarm_after = iso8601.parse_date(deadline)
    delta = alarm_after - now
    signal.signal(signal.SIGALRM, timeout_func)
    signal.alarm(int(delta.total_seconds()))

    try:
        result = handle_func(ctx, data=data)
        if isinstance(result, types.CoroutineType):
            signal.alarm(0)
            return await result

        signal.alarm(0)
        return result
    except (Exception, TimeoutError) as ex:
        signal.alarm(0)
        raise ex


async def from_request(handle_func, incoming_request):
    print("request parsed", file=sys.stderr, flush=True)

    call_id = incoming_request.get("call_id")
    app = os.environ.get("FN_APP_NAME")
    path = os.environ.get("FN_PATH")
    content_type = incoming_request.get("content_type")
    protocol = incoming_request.get("protocol", {
        "headers": {},
        "type": "http",
        "method": "GET",
        "request_url": "{0}{1}".format(app, path),
    })

    json_headers = headers.GoLikeHeaders(protocol.get("headers"))
    call_type = json_headers.get("fn-type", "sync")

    ctx = context.JSONContext(app, path, call_id,
                              content_type=content_type,
                              execution_type=call_type,
                              deadline=incoming_request.get("deadline"),
                              config=os.environ, headers=json_headers)

    print("context allocated", file=sys.stderr, flush=True)
    print("starting the function", file=sys.stderr, flush=True)
    print(incoming_request.get("body"), file=sys.stderr, flush=True)

    response_data = await with_deadline(
        ctx, handle_func, incoming_request.get("body"))

    if isinstance(response_data, response.RawResponse):
        return response_data

    print("the function finished", file=sys.stderr, flush=True)
    return response.RawResponse(
        ctx, response_data=response_data, status_code=200)


async def handle_request(handle_func, data):

    try:
        print("entering handle_request", file=sys.stderr, flush=True)
        return await from_request(handle_func, data)

    except (Exception, TimeoutError) as ex:
        traceback.print_exc(file=sys.stderr)
        status = 502 if isinstance(ex, TimeoutError) else 500
        return errors.JSONDispatchException(
            context, status, str(ex)).response()


def read_json(stream) -> bytes:

    line = bytes()
    ret = False

    while True:
        c = stream.read(1)
        if c is None:
            continue
        if len(c) == 0:
            print("Before JSON parsing: {}".format(line),
                  file=sys.stderr, flush=True)
            return ujson.loads(line)

        if c.decode() == "}":
            line += c
            ret = True
        elif c.decode() == "\n" and ret:
            line += c
            print("Before JSON parsing: {}".format(line),
                  file=sys.stderr, flush=True)
            return ujson.loads(line)
        else:
            ret = False
            line += c
