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
import os
import uvloop

from fdk import constants
from fdk import runner
from fdk import http_stream


def handle(handle_func):
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()

    format_def = os.environ.get("FN_FORMAT")
    lsnr = os.environ.get("FN_LISTENER", "unix:/iofs/lsnr.sock")

    if format_def == constants.HTTPSTREAM:
        http_stream.start(handle_func, lsnr, loop=loop)
    else:
        with open("/dev/stdin", "rb", buffering=0) as stdin:
            while True:
                f = runner.handle_request(
                    handle_func, stdin, format_def)
                response = loop.run_until_complete(f)
                response.dump()
