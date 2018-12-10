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

import h11

from fdk import constants
from fdk import log


def process_chunk(connection):
    request, body = None, None
    while True:
        event = connection.next_event()
        if isinstance(event, h11.Request):
            request = event
        if isinstance(event, h11.Data):
            body = event
        if isinstance(event, h11.EndOfMessage):
            return request, body
        if isinstance(event, (h11.NEED_DATA, h11.PAUSED)):
            break
        if isinstance(event, h11.ConnectionClosed):
            raise Exception("connection closed")


async def read_request(connection, request_reader):
    raw_data = b""
    while True:
        raw_data += await request_reader.read(constants.IO_LIMIT)
        connection.receive_data(raw_data)
        request, body = process_chunk(connection)
        if request is None:
            raise Exception("unable to read incoming request")
        return request, body


async def write_response(connection, func_response, response_writer):
    headers = func_response.ctx.GetResponseHeaders().items()
    status = func_response.status()
    log.log("response headers: {}".format(headers))
    log.log("response status: {}".format(status))
    response_writer.write(
        connection.send(h11.Response(
            status_code=status, headers=headers)
        )
    )

    response_writer.write(connection.send(
        h11.Data(
            data=str(func_response.body()).encode("utf-8")))
    )
    response_writer.write(connection.send(h11.EndOfMessage()))
    await response_writer.drain()
