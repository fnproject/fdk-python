#
# Copyright (c) 2019, 2020 Oracle and/or its affiliates. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import io
import sys
import traceback
import types

from fdk import context
from fdk import customer_code
from fdk import errors
from fdk import log
from fdk import response


async def with_deadline(ctx: context.InvokeContext,
                        handler_code: customer_code.Function,
                        data: io.BytesIO):
    """
    Runs function within a timer
    :param ctx: invoke context
    :type ctx: fdk.context.InvokeContext
    :param handler_code: customer's code
    :type handler_code: fdk.customer_code.Function
    :param data: request data stream
    :type data: io.BytesIO
    :return:
    """

    # ctx.Deadline() would never be an empty value,
    # by default it will be 30 secs from now

    try:
        handle_func = handler_code.handler()
        result = handle_func(ctx, data=data)
        if isinstance(result, types.CoroutineType):
            return await result

        return result
    except (Exception, TimeoutError) as ex:
        raise ex


async def handle_request(handler_code, format_def, **kwargs):
    """
    Handles a function's request
    :param handler_code: customer's code
    :type handler_code: fdk.customer_code.Function
    :param format_def: function's format
    :type format_def: str
    :param kwargs: request-specific parameters
    :type kwargs: dict
    :return: function's response
    :rtype: fdk.response.Response
    """
    log.log("in handle_request")
    ctx, body = context.context_from_format(format_def, **kwargs)
    log.set_request_id(ctx.CallID())
    log.log("context provisioned")
    try:
        response_data = await with_deadline(ctx, handler_code, body)
        log.log("function result obtained")
        if isinstance(response_data, response.Response):
            return response_data
        headers = ctx.GetResponseHeaders()
        log.log("response headers obtained")
        return response.Response(
            ctx, response_data=response_data,
            headers=headers, status_code=200)

    except TimeoutError as ex:
        log.log("Function timeout: {}".format(ex))
        (exctype, value, tb) = sys.exc_info()
        tb_flat = ''.join(
            s.replace('\n', '\\n') for s in traceback.format_tb(tb))
        log.get_request_log().error('{}:{}'.format(value, tb_flat))
        return errors.DispatchException(ctx, 504, str(ex)).response()
    except Exception as ex:
        log.log("exception appeared: {0}".format(ex))
        (exctype, value, tb) = sys.exc_info()
        tb_flat = ''.join(
            s.replace('\n', '\\n') for s in traceback.format_tb(tb))
        log.get_request_log().error('{}:{}'.format(value, tb_flat))
        return errors.DispatchException(ctx, 502, str(ex)).response()
