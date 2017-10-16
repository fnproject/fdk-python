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

import fdk
import sys
import traceback

from fdk.http import response


def exception_to_string(err):
    stack = (traceback.extract_stack()[:-3] +
             traceback.extract_tb(err.__traceback__))
    pretty = traceback.format_list(stack)
    return (''.join(pretty) +
            '\n  {} {}'.format(err.__class__, err))


def handler(context, data=None, loop=None):
    """
    This is just an echo function
    :param context: request context
    :type context: hotfn.http.request.RequestContext
    :param data: request body
    :type data: object
    :param loop: asyncio event loop
    :type loop: asyncio.AbstractEventLoop
    :return: echo of request body
    :rtype: object
    """
    headers = {
        "Content-Type": "text/plain",
    }
    rs = response.RawResponse(
        http_proto_version=context.version,
        status_code=200,
        headers=headers,
        response_data="OK"
    )
    print("response created", file=sys.stderr, flush=True)
    try:
        raise Exception("test-exception")
    except Exception as ex:
        print("exception raised", file=sys.stderr, flush=True)
        rs.status_code = 500
        rs.set_response_content(exception_to_string(ex))

    return rs


if __name__ == "__main__":
    fdk.handle(handler)
