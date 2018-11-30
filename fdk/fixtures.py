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

import datetime as dt

from fdk import constants


class stream(object):

    def __init__(self, data):
        if data is None:
            self.data = b''
        else:
            self.data = data

    async def read(self, n=-1):
        if n < 0:
            return self.data
        if n >= len(self.data):
            return self.data

        return self.data[n:]

    async def readall(self):
        return await self.read()


async def process_response(fn_call):
    from fdk import headers as hs
    new_headers = {}
    resp = await fn_call
    headers = resp.context().GetResponseHeaders()
    for k, v in dict(headers).items():
        new_headers.update({
            k.lstrip(constants.FN_HTTP_PREFIX): v
        })
    content = resp.body()
    resp_headers = hs.decap_headers(headers)
    status = int(headers.get(constants.FN_HTTP_STATUS))
    del resp_headers[constants.FN_HTTP_STATUS]
    return content, status, resp_headers


async def setup_fn_call(handle_func,
                        request_url="/", method="POST",
                        headers=None, json=None,
                        deadline=None):
    import ujson
    from fdk import runner

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
        constants.FN_CALL_ID: "py.test"
    })
    sr = stream(None)
    if json:
        sr.data = ujson.dumps(json).encode("utf-8")

    return await runner.handle_request(
        handle_func, constants.HTTPSTREAM,
        headers=new_headers, data=sr
    )
