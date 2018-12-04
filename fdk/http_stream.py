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
import h11
import io
import os
import ujson

from fdk import constants
from fdk import log
from fdk import runner


def handle(handle_code):
    async def pure_handler(request_reader, response_writer):
        s = h11.Connection(h11.SERVER)

        # read exactly 10Mb
        raw_data = await request_reader.read(10485760)
        s.receive_data(raw_data)
        events_map = {}
        while True:
            event = s.next_event()
            if isinstance(event, h11.Request):
                events_map["request"] = event
            if isinstance(event, h11.Data):
                events_map["data"] = event
            elif (isinstance(event, h11.ConnectionClosed) or
                  event is h11.NEED_DATA or event is h11.PAUSED):
                break

        log.log("in pure_handler")
        request = events_map["request"]
        body = events_map.get("data")
        data = None
        if body:
            data = body.data
        headers = dict(request.headers)

        func_response = await runner.handle_request(
            handle_code, constants.HTTPSTREAM,
            headers=headers, data=io.BytesIO(data))
        log.log("request execution completed")

        response_writer.write(
            s.send(h11.Response(
                status_code=func_response.status(),
                headers=func_response.ctx.GetResponseHeaders().items())
            )
        )

        response_writer.write(s.send(
            h11.Data(
                data=str(func_response.body()).encode("utf-8")))
        )
        response_writer.write(s.send(h11.EndOfMessage()))
        await response_writer.drain()

    return pure_handler


def start(handle_code, uds, loop=None):
    log.log("in http_stream.start")
    socket_path = str(uds).lstrip("unix:")

    # setting up app runner
    log.log("setting app_runner")

    # try to remove pre-existing UDS: ignore errors here
    socket_dir, socket_file = os.path.split(socket_path)
    phony_socket_path = os.path.join(
        socket_dir, "phony" + socket_file)

    log.log("deleting socket files if they exist")
    try:
        os.remove(socket_path)
        os.remove(phony_socket_path)
    except (FileNotFoundError, Exception, BaseException):
        pass

    log.log("starting unix socket site")
    unix_srv = loop.run_until_complete(
        asyncio.start_unix_server(
            handle(handle_code),
            path=phony_socket_path,
            loop=loop)
    )
    try:
        try:
            log.log("CHMOD 666 {0}".format(phony_socket_path))
            os.chmod(phony_socket_path, 0o666)
            log.log("phony socket permissions: {0}"
                    .format(oct(os.stat(phony_socket_path).st_mode)))
            log.log("sym-linking {0} to {1}".format(
                socket_path, phony_socket_path))
            os.symlink(os.path.basename(phony_socket_path), socket_path)
            log.log("socket permissions: {0}"
                    .format(oct(os.stat(socket_path).st_mode)))
            log.log("starting infinite loop")
            loop.run_forever()
        except (Exception, BaseException) as ex:
            log.log(str(ex))
            raise ex
    finally:
        if hasattr(loop, 'shutdown_asyncgens'):
            loop.run_until_complete(loop.shutdown_asyncgens())
        unix_srv.close()
        loop.run_until_complete(unix_srv.wait_closed())
        loop.close()
