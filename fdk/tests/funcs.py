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

import time
import ujson

from fdk import response


def dummy_func(ctx, data=None):
    body = ujson.loads(data) if len(data) > 0 else {"name": "World"}
    return "Hello {0}".format(body.get("name"))


def content_type(ctx, data=None):
    return response.RawResponse(
        ctx, response_data="OK", status_code=200,
        headers={"content-type": "application/xml"})


def custom_response(ctx, data=None):
    return response.RawResponse(
        ctx, response_data=dummy_func(ctx, data=data), status_code=201)


def expectioner(ctx, data=None):
    raise Exception("custom_error")


def none_func(ctx, data=None):
    return


def timed_sleepr(timeout):

    def sleeper(ctx, data=None):
        time.sleep(timeout)

    return sleeper


async def coro(ctx, **kwargs):
    return "hello from coro"
