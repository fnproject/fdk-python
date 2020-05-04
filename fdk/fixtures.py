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
from fdk import runner
from fdk import headers as hs


async def process_response(fn_call_coro):
    resp = await fn_call_coro
    response_data = resp.body()
    response_status = resp.status()
    response_headers = resp.context().GetResponseHeaders()

    return response_data, response_status, response_headers


class fake_request(object):

    def __init__(self, gateway=False):
        self.headers = setup_headers(gateway=gateway)
        self.body = b''


class code(object):

    def __init__(self, fn):
        self.fn = fn

    def handler(self):
        return self.fn


def setup_headers(deadline=None, headers=None,
                  request_url="/", method="POST", gateway=False):
    new_headers = {}

    if gateway:
        new_headers = hs.encap_headers(headers)
        new_headers.update({
            constants.FN_INTENT: constants.INTENT_HTTP_REQUEST,
        })
    elif headers is not None:
        for k, v in headers.items():
            new_headers.update({k: v})

    new_headers.update({
        constants.FN_HTTP_REQUEST_URL: request_url,
        constants.FN_HTTP_METHOD: method,
    })

    if deadline is None:
        now = dt.datetime.now(dt.timezone.utc).astimezone()
        now += dt.timedelta(0, float(constants.DEFAULT_DEADLINE))
        deadline = now.isoformat()

    new_headers.update({constants.FN_DEADLINE: deadline})
    return new_headers


async def setup_fn_call(
        handle_func, request_url="/",
        method="POST", headers=None,
        content=None, deadline=None,
        gateway=False):

    new_headers = setup_headers(
        deadline=deadline, headers=headers,
        method=method, request_url=request_url,
        gateway=gateway
    )
    return await setup_fn_call_raw(handle_func, content, new_headers)


async def setup_fn_call_raw(handle_func, content=None, headers=None):

    if headers is None:
        headers = {}

    # don't decap headers, so we can test them
    # (just like they come out of fdk)
    return process_response(runner.handle_request(
        code(handle_func), constants.HTTPSTREAM,
        headers=headers, data=content,
    ))
