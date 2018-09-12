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

from aiohttp import web

from fdk import constants
from fdk import runner


def handle(handle_func):
    async def pure_handler(request):
        data = None
        if (request.has_body and
                request.content_length is not None and
                request.content_length > 0):
            data = request.content.read(request.content_length)

        response = await runner.handle_request(
            handle_func, None, constants.HTTPSTREAM,
            request=request, data=data)
        # check content type and response data type

        return web.Response(
            body=response.body(),
            status=response.status(),
            headers=response.headers().http_raw(),
        )

    return pure_handler


def setup_unix_server(handle_func, loop=None):
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
    app = setup_unix_server(handle_func, loop=loop)
    web.run_app(app, path=uds[len("unix:/"):], shutdown_timeout=1.0)
