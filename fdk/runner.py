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

import io
import sys
import traceback
import signal
import datetime as dt
import iso8601
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

    def timeout_func(*_):
        raise TimeoutError("function timed out")

    now = dt.datetime.now(dt.timezone.utc).astimezone()
    # ctx.Deadline() would never be an empty value,
    # by default it will be 30 secs from now
    deadline = ctx.Deadline()
    alarm_after = iso8601.parse_date(deadline)
    delta = alarm_after - now
    signal.signal(signal.SIGALRM, timeout_func)
    signal.alarm(int(delta.total_seconds()))

    try:
        handle_func = handler_code.handler()
        result = handle_func(ctx, data=data)
        if isinstance(result, types.CoroutineType):
            signal.alarm(0)
            return await result

        signal.alarm(0)
        return result
    except (Exception, TimeoutError) as ex:
        signal.alarm(0)
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

    except (Exception, TimeoutError) as ex:
        log.log("exception appeared: {0}".format(ex))
        traceback.print_exc(file=sys.stderr)
        return errors.DispatchException(ctx, 502, str(ex)).response()
