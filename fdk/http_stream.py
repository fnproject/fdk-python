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
import ujson

from aiohttp import web
from xml.etree import ElementTree

from fdk import constants
from fdk import headers as hs
from fdk import log
from fdk import runner
from fdk import response as rtypes


def serialize_response_data(data, content_type):
    log.log("in serialize_response_data")
    if data:
        if "application/json" in content_type:
            return bytes(ujson.dumps(data), "utf8")
        if "text/plain" in content_type:
            return bytes(str(data), "utf8")
        if "application/xml" in content_type:
            # returns a bytearray
            if isinstance(data, str):
                return bytes(data, "utf8")
            return ElementTree.tostring(data, encoding='utf8', method='xml')
        if "application/octet-stream" in content_type:
            return data
    return


def encap_headers(headers, status, content_type):
    new_headers = hs.GoLikeHeaders({})
    for k, v in headers.items():
        if "content_type" not in k:
            new_headers.set(constants.FN_HTTP_PREFIX + k, v)

    new_headers.set("Fn-Http-Status", str(status))
    new_headers.set("Content-Type", content_type)
    return new_headers


def handle(handle_func):
    async def pure_handler(request):
        log.log("in pure_handler")
        data = None
        if (request.has_body and
                request.content_length is not None and
                request.content_length > 0):
            log.log("request comes with data")
            data = await request.content.read(request.content_length)
        response = await runner.handle_request(
            handle_func, None, constants.HTTPSTREAM,
            request=request, data=data)
        log.log("request execution completed")
        headers = (response.headers()
                   if isinstance(response, rtypes.RawResponse)
                   else response.headers)
        response_content_type = headers.get(
            "content-type", "application/json"
        )
        headers.delete("content-type")

        headers = encap_headers(
            headers, response.status(), response_content_type)
        kwargs = {
            "status": response.status(),
            "headers": headers.http_raw()
        }

        sdata = serialize_response_data(
            response.body(), response_content_type)

        if response.status() >= 500:
            kwargs.update(reason=sdata)
        else:
            kwargs.update(body=sdata)

        log.log("sending response back")
        try:
            resp = web.Response(**kwargs)
        except (Exception, BaseException) as ex:

            resp = web.Response(
                text=str(ex), reason=str(ex),
                status=500, content_type="text/plain", headers={
                    "Fn-Http-Status": str(500)
                })

        return resp

    return pure_handler


def setup_unix_server(handle_func, loop=None):
    log.log("in setup_unix_server")
    app = web.Application(loop=loop)

    app.router.add_post('/{tail:.*}', handle(handle_func))

    return app


def start(handle_func, uds, loop=None):
    log.log("in http_stream.start")
    app = setup_unix_server(handle_func, loop=loop)

    socket_path = str(uds).lstrip("unix:")

    if asyncio.iscoroutine(app):
        app = loop.run_until_complete(app)

    log.log("socket file exist? - {0}"
            .format(os.path.exists(socket_path)))
    app_runner = web.AppRunner(
        app, handle_signals=True,
        access_log=log.get_logger())

    # setting up app runner
    log.log("setting app_runner")
    loop.run_until_complete(app_runner.setup())

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
    uds_sock = web.UnixSite(
        app_runner, phony_socket_path,
        shutdown_timeout=0.1)
    loop.run_until_complete(uds_sock.start())
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
        try:
            log.log("starting infinite loop")
            loop.run_forever()
        except web.GracefulExit:
            pass
    finally:
        loop.run_until_complete(app_runner.cleanup())
    if hasattr(loop, 'shutdown_asyncgens'):
        loop.run_until_complete(loop.shutdown_asyncgens())
    loop.close()
