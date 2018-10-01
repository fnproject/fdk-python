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

import sys
import traceback
import signal
import datetime as dt
import iso8601
import types

from fdk import context
from fdk import errors
from fdk import log
from fdk import response


# TODO(xxx): use loop.run_in_executor instead
async def with_deadline(ctx, handle_func, data):

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
        result = handle_func(ctx, data=data)
        if isinstance(result, types.CoroutineType):
            signal.alarm(0)
            return await result

        signal.alarm(0)
        return result
    except (Exception, TimeoutError) as ex:
        signal.alarm(0)
        raise ex


async def handle_request(handle_func, format_def, **kwargs):

    ctx, body = context.context_from_format(format_def, **kwargs)

    try:
        response_data = await with_deadline(ctx, handle_func, body)

        if isinstance(response_data, response.RawResponse):
            return response_data

        resp_class = response.response_class_from_context(ctx)
        return resp_class(
            ctx, response_data=response_data, headers={}, status_code=200)

    except (Exception, TimeoutError) as ex:
        log.log("exception appeared")
        traceback.print_exc(file=sys.stderr)
        status = 502 if isinstance(ex, TimeoutError) else 500
        err_class = errors.error_class_from_format(format_def)
        return err_class(ctx, status, str(ex), ).response()
