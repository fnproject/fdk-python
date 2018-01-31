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

import contextlib
import datetime as dt
import iso8601
import os
import signal
import sys

from fdk import context
from fdk.http import handle as http_handle
from fdk.http import request as http_request
from fdk.json import handle as json_handle
from fdk.json import request as json_request


def generic_handle(handler, loop=None):
    """
    Request handler app dispatcher entry point
    :param handler: request handler app
    :type handler: types.Callable
    :param loop: asyncio event loop
    :type loop: asyncio.AbstractEventLoop
    :return: None
    """
    fn_format = os.environ.get("FN_FORMAT")
    (request_class,
     stream_reader_mode, stream_writer_mode, dispatcher) = (
        None, "rb", "wb", None)

    if fn_format in [None, "default"]:
        exit(501)

    if fn_format == "json":
        (request_class,
         stream_reader_mode,
         stream_writer_mode, dispatcher) = (
            json_request.RawRequest,
            "r", "w",
            json_handle.normal_dispatch)

    if fn_format == "http":
        (request_class,
         stream_reader_mode,
         stream_writer_mode, dispatcher) = (
            http_request.RawRequest,
            "rb", "wb",
            http_handle.normal_dispatch)

    if not os.isatty(sys.stdin.fileno()):
        with os.fdopen(sys.stdin.fileno(), stream_reader_mode) as read_stream:
            with os.fdopen(sys.stdout.fileno(),
                           stream_writer_mode) as write_stream:
                request = request_class(read_stream)
                while True:
                    proceed_with_streams(handler, request, write_stream,
                                         dispatcher, loop=loop)


@contextlib.contextmanager
def timeout(request, write_stream):

    def handler(*_):
        raise TimeoutError("Function timed out")

    fn_format = os.environ.get("FN_FORMAT")
    ctx = context.fromType(fn_format,
                           os.environ.get("FN_APP_NAME"),
                           os.environ.get("FN_PATH"), "",)

    try:
        ctx, data = request.parse_raw_request()

        deadline = ctx.Deadline()
        alarm_after = iso8601.parse_date(deadline)
        now = dt.datetime.now(dt.timezone.utc).astimezone()
        delta = alarm_after - now
        signal.signal(signal.SIGALRM, handler)
        signal.alarm(int(delta.total_seconds()))

        yield (ctx, data)

    except EOFError:
        # pipe closed from the other side by Fn
        return
    except ctx.DispatchError as ex:
        signal.alarm(0)
        ex.response().dump(write_stream)
        return


def proceed_with_streams(handler, request, write_stream,
                         dispatcher, loop=None):
    """
    Handles both request parsing and dumping
    :param handler: request body handler
    :param request: incoming request
    :param write_stream: write stream (usually STDOUT)
    :param dispatcher: raw HTTP/JSON request dispatcher
    :param loop: asyncio event loop
    :return:
    """

    with timeout(request, write_stream) as (ctx, data):
        rs = dispatcher(handler, ctx,
                        data=data, loop=loop)
        rs.dump(write_stream)
