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
import datetime as dt

from fdk import constants
from fdk import headers as hs
from fdk import http_stream


async def process_response(fn_call_coro):
    new_headers = {}
    resp = await fn_call_coro
    for k, v in dict(resp.headers).items():
        new_headers.update({
            k.lstrip(constants.FN_HTTP_PREFIX): v
        })
    content = await resp.content.read()
    resp_headers = hs.decap_headers(resp.headers)
    status = int(resp.headers.get(constants.FN_HTTP_STATUS))
    resp_headers.delete(constants.FN_HTTP_STATUS)
    return content, status, resp_headers


async def setup_fn_call(fn_client, handle_func,
                        request_url="/", method="POST",
                        headers=None, json=None,
                        deadline=None):
    app = http_stream.setup_unix_server(
        handle_func,
        loop=asyncio.get_event_loop()
    )

    new_headers = {}
    if headers is not None:
        for k, v in headers.items():
            new_headers.update({constants.FN_HTTP_PREFIX + k: v})

    if deadline is None:
        now = dt.datetime.now(dt.timezone.utc).astimezone()
        now += dt.timedelta(0, float(constants.DEFAULT_DEADLINE))
        deadline = now.isoformat()

    new_headers.update({
        constants.FN_DEADLINE: deadline,
        constants.FN_HTTP_REQUEST_URL: request_url,
        constants.FN_HTTP_METHOD: method,
    })

    client = await fn_client(app)
    return process_response(
        client.post("/call", headers=new_headers, json=json))
