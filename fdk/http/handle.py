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
import json
import types

from fdk import errors
from fdk.http import response


def normal_dispatch(app, context, data=None, loop=None):
    """
    Request handler app dispatcher
    :param app: request handler app
    :type app: types.Callable
    :param context: request context
    :type context: request.RequestContext
    :param data: request body
    :type data: io.BufferedIOBase
    :param loop: asyncio event loop
    :type loop: asyncio.AbstractEventLoop
    :return: raw response
    :rtype: response.RawResponse
    """
    try:
        rs = app(context, data=data, loop=loop)
        if isinstance(rs, response.RawResponse):
            return rs
        elif isinstance(rs, types.CoroutineType):
            return loop.run_until_complete(rs)
        elif isinstance(rs, str):
            return response.RawResponse(http_proto_version=context.version,
                                        status_code=200,
                                        headers={},
                                        response_data=rs)
        elif isinstance(rs, bytes):
            return response.RawResponse(
                http_proto_version=context.version,
                status_code=200,
                headers={'content-type': 'application/octet-stream'},
                response_data=rs.decode("utf8"))
        else:
            return response.RawResponse(
                http_proto_version=context.version,
                status_code=200,
                headers={'content-type': 'application/json'},
                response_data=json.dumps(rs))
    except errors.HTTPDispatchException as e:
        return e.response()
    except Exception as e:
        return response.RawResponse(
            http_proto_version=context.version,
            status_code=500,
            headers={},
            response_data=str(e))


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
        # TODO(jang): The content-type header has some internal structure;
        # actually provide some parsing for that
        content_type = context.headers.get("content-type")
        try:
            request_body = io.TextIOWrapper(data)
            # TODO(denismakogon): XML type to add
            if content_type == "application/json":
                body = json.load(request_body)
            elif content_type in ["text/plain"]:
                body = request_body.read()
            else:
                body = request_body.read()
        except Exception as ex:
            raise errors.HTTPDispatchException(
                500, "Unexpected error: {}".format(str(ex)))

        return request_data_processor(context, data=body, loop=loop)

    return app
