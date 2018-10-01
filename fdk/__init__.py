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
import sys

from fdk import constants
from fdk import log
from fdk import http_stream


def handle(handle_func):
    log.log("entering handle")
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()

    format_def = os.environ.get(constants.FN_FORMAT)
    lsnr = os.environ.get(constants.FN_LISTENER)
    log.log("format: {0}".format(format_def))

    if format_def == constants.HTTPSTREAM:
        if lsnr is None:
            log.log("{0} is not set".format(constants.FN_LISTENER))
            sys.exit(1)
        log.log("{0} is set, value: {1}".
                format(constants.FN_LISTENER, lsnr))
        http_stream.start(handle_func, lsnr, loop=loop)
    else:
        log.log("incompatible function format!")
        print("incompatible function format!", file=sys.stderr, flush=True)
        sys.exit("incompatible function format!")
