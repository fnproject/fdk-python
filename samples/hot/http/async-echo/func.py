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

import fdk
from fdk import response


@fdk.coerce_input_to_content_type
async def app(context, data=None, loop=None):
    """
    This is just an echo function
    :param context: request context
    :type context: fdk.context.RequestContext
    :param data: request body
    :type data: object
    :param loop: asyncio event loop
    :type loop: asyncio.AbstractEventLoop
    :return: echo of request body
    :rtype: object
    """
    headers = {
        "Content-Type": "plain/text",
    }
    return response.RawResponse(
        context,
        status_code=200,
        headers=headers,
        response_data="OK")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    fdk.handle(app, loop=loop)
