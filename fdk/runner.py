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
import sys
import ujson
import os
import traceback
import types

from fdk import context
from fdk import errors
from fdk import headers
from fdk import response


def handle_callable(ctx, handle_func, data=None,
                    loop: asyncio.AbstractEventLoop=None):
    r = handle_func(ctx, data=data, loop=loop)

    if isinstance(r, types.CoroutineType):
        print("function appeared to be a coroutine, awaiting...",
              file=sys.stderr, flush=True)
        print("loop state: ", str(loop.is_running()),
              file=sys.stderr, flush=True)
        while not loop.is_running():
            return loop.run_until_complete(r)
    else:
        return r


def from_request(handle_func, incoming_request, loop=None):
    print("request parsed", file=sys.stderr, flush=True)
    json_headers = headers.GoLikeHeaders(
        incoming_request.get('protocol', {"headers": {}}).get("headers"))

    print("headers parsed", file=sys.stderr, flush=True)
    ctx = context.JSONContext(os.environ.get("FN_APP_NAME"),
                              os.environ.get("FN_PATH"),
                              incoming_request.get("call_id"),
                              execution_type=incoming_request.get(
                                  "type", "sync"),
                              deadline=incoming_request.get("deadline"),
                              config=os.environ, headers=json_headers)

    print("context allocated", file=sys.stderr, flush=True)
    print("starting the function", file=sys.stderr, flush=True)
    print(incoming_request.get("body"), file=sys.stderr, flush=True)
    response_data = handle_callable(
        ctx, handle_func, data=incoming_request.get("body"), loop=loop)

    if isinstance(response_data, response.RawResponse):
        return response_data

    print("the function finished", file=sys.stderr, flush=True)
    return response.RawResponse(
        ctx, response_data=response_data, status_code=200)


def handle_request(handle_func, data, loop=None):
    try:
        print("entering handle_request", file=sys.stderr, flush=True)
        incoming_json = ujson.loads(str(data.decode('utf8').replace("'", '"')))

        return from_request(handle_func, incoming_json, loop=loop)

    except (Exception, TimeoutError) as ex:
        traceback.print_exc(file=sys.stderr)
        status = 502 if isinstance(ex, TimeoutError) else 500
        return errors.JSONDispatchException(
            context, status, str(ex)).response()


class JSONProtocol(asyncio.Protocol):

    handle_func = None
    loop = None

    @classmethod
    def with_handler(cls, handler_func, loop=None):
        cls.handle_func = handler_func
        cls.loop = loop
        return cls

    def connection_made(self, transport):
        print('pipe opened', file=sys.stderr, flush=True)
        super(JSONProtocol, self).connection_made(transport=transport)

    def data_received(self, data):
        print('received: ', data.decode(), file=sys.stderr, flush=True)

        rs = handle_request(
            self.__class__.handle_func, data, loop=self.__class__.loop)
        print("response created", file=sys.stderr, flush=True)
        rs.dump()

        super(JSONProtocol, self).data_received(data)

    def connection_lost(self, exc):
        print('pipe closed', file=sys.stderr, flush=True)
        super(JSONProtocol, self).connection_lost(exc)
        sys.exit(0)
