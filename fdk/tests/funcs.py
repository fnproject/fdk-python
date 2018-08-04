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


xml = """<!DOCTYPE mensaje SYSTEM "record.dtd">
<record>
    <player_birthday>1979-09-23</player_birthday>
    <player_name>Orene Ai'i</player_name>
    <player_team>Blues</player_team>
    <player_id>453</player_id>
    <player_height>170</player_height>
    <player_position>FW</player_position>
    <player_weight>75</player_weight>
</record>"""


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


def valid_xml(ctx, **kwargs):
    return response.RawResponse(
        ctx, response_data=xml, headers={
            "content-type": "application/xml",
        }
    )


def invalid_xml(ctx, **kwargs):
    return response.RawResponse(
        ctx, response_data=ujson.dumps(xml), headers={
            "content-type": "application/xml",
        }
    )


def verify_request_headers(ctx, **kwargs):
    return response.RawResponse(
        ctx,
        response_data=ujson.dumps(xml),
        headers=ctx.Headers()
    )
