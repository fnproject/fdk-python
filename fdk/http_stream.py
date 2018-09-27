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

    for m in [app.router.add_get,
              app.router.add_post,
              app.router.add_put,
              app.router.add_patch,
              app.router.add_delete,
              app.router.add_head]:
        m('/{tail:.*}', handle(handle_func))

    return app


def start(handle_func, uds, loop=None):
    log.log("in htt_stream.start")
    app = setup_unix_server(handle_func, loop=loop)
    web.run_app(app, path=uds[len("unix:"):],
                shutdown_timeout=1.0,
                access_log=log.get_logger())
