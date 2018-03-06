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

import functools
import io
import ujson

from fdk import runner

handle = runner.generic_handle


def coerce_input_to_content_type(request_data_processor):

    @functools.wraps(request_data_processor)
    def app(context, data=None, loop=None):
        """
        Request handler app dispatcher decorator
        :param context: request context
        :type context: request.RequestContext
        :param data: request body
        :type data: io.BufferedIOBase
        :param loop: asyncio event loop
        :type loop: asyncio.AbstractEventLoop
        :return: raw response
        :rtype: response.RawResponse
        :return:
        """
        body = data
        content_type = context.Headers().get("content-type")
        try:

            if hasattr(data, "readable"):
                request_body = io.TextIOWrapper(data)
            else:
                request_body = data

            if content_type == "application/json":
                if isinstance(request_body, str):
                    if len(request_body) > 0:
                        body = ujson.loads(request_body)
                    else:
                        body = {}
                else:
                    body = ujson.load(request_body)
            elif content_type in ["text/plain"]:
                body = request_body.read()

        except Exception as ex:
            raise context.DispatchError(
                context, 500, "Unexpected error: {}".format(str(ex)))

        return request_data_processor(context, data=body, loop=loop)

    return app


__all__ = [
    'handle'
]
