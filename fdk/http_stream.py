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
import os

from fdk import constants
from fdk import log
from fdk import runner
from fdk.http import request
from fdk.http import response


def handle(handle_func):
    async def pure_handler(reader, writer):
        try:
            raw_r = request.RawRequest(reader)
            (protocol, path, method,
             params, headers, body) = await raw_r.parse_raw_request()

            log.log(protocol)
            log.log(path)
            log.log(method)
            log.log(params)
            log.log(headers)
            log.log(body)
        except (EOFError, ValueError) as ex:
            rsp = response.RawResponse(
                (1, 1),
                status_code=5000,
                headers={
                    constants.CONTENT_TYPE: "text/plan",
                    constants.CONTENT_LENGTH: len(str(ex))
                },
                response_data=str(ex))
            await rsp.dump(writer, flush=True)
            return

        resp = await runner.handle_request(
            handle_func, constants.HTTPSTREAM,
            headers=headers, data=body)

        resp.body()
        hs = resp.context().GetResponseHeaders()
        rsp = response.RawResponse(
            protocol,
            status_code=resp.status(),
            headers=hs,
            response_data=resp.body())
        await rsp.dump(writer, flush=True)

    return pure_handler


def start(handle_func, uds, loop=None):
    log.log("in http_stream.start")
    socket_path = str(uds).lstrip("unix:")
    log.log("socket file exist? - {0}"
            .format(os.path.exists(socket_path)))

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
    server = loop.run_until_complete(
        asyncio.start_unix_server(
            handle(handle_func),
            path=phony_socket_path,
            loop=loop
        )
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
        except (Exception, BaseException) as ex:
            log.log(str(ex))
            raise ex

        log.log("starting dispatch in event loop")
        loop.run_forever()
    finally:
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()

    if hasattr(loop, 'shutdown_asyncgens'):
        loop.run_until_complete(loop.shutdown_asyncgens())
    loop.close()
