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

import os
import sys
import traceback

from fdk import errors

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
    (exc_class, request_class,
     stream_reader_mode, stream_writer_mode, dispatcher) = (
        None, None, "rb", "wb", None)

    fn_format = os.environ.get("FN_FORMAT")

    if fn_format == "json":
        (exc_class,
         request_class,
         stream_reader_mode,
         stream_writer_mode, dispatcher) = (
            errors.JSONDispatchException,
            json_request.RawRequest,
            "r", "w",
            json_handle.normal_dispatch)

    if fn_format == "http":
        (exc_class,
         request_class,
         stream_reader_mode,
         stream_writer_mode, dispatcher) = (
            errors.HTTPDispatchException,
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
                                         dispatcher, exc_class, loop=loop)


def proceed_with_streams(handler, request, write_stream,
                         dispatcher, exc_class, loop=None):
    """
    Handles both request parsing and dumping
    :param handler: request body handler
    :param request: incoming request
    :param write_stream: write stream (usually STDOUT)
    :param dispatcher: raw HTTP/JSON request dispatcher
    :param exc_class: HTTP/JSON exception class
    :param loop: asyncio event loop
    :return:
    """
    try:
        context, data = request.parse_raw_request()
        rs = dispatcher(handler, context,
                        data=data, loop=loop)
        rs.dump(write_stream)
    except EOFError:
        # pipe closed from the other side by Fn
        return
    except exc_class as ex:
        ex.response().dump(write_stream)
    except Exception as ex:
        traceback.print_exc(file=sys.stderr)
        exc_class(500, str(ex)).response().dump(write_stream)
