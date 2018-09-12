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

from fdk import http_stream

from fdk.tests import funcs


async def test_override_content_type(aiohttp_client):
    app = http_stream.setup_unix_server(
        funcs.content_type,
        loop=asyncio.get_event_loop(),
    )

    client = await aiohttp_client(app, )
    resp = await client.get("/r/app/route")
    resp_data = await resp.text()

    assert resp.status == 200
    assert "OK" == resp_data
    assert "application/xml" in resp.headers.get("Content-Type")
