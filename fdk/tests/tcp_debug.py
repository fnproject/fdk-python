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
import uvloop

from fdk import constants
from fdk import customer_code
from fdk import log
from fdk.http import event_handler


def handle(handle_func: customer_code.Function, port: int=5000):
    """
    FDK entry point
    :param handle_func: customer's code
    :type handle_func: fdk.customer_code.Function
    :param port: TCP port to start an FDK at
    :type port: int
    :return: None
    """
    host = "localhost"
    log.log("entering handle")
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    log.log("Starting HTTP server on "
            "TCP socket: {0}:{1}".format(host, port))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        asyncio.start_server(
            event_handler.event_handle(handle_func),
            host=host, port=port,
            limit=constants.IO_LIMIT, loop=loop)
    )
    try:
        loop.run_forever()
    finally:
        if hasattr(loop, 'shutdown_asyncgens'):
            loop.run_until_complete(loop.shutdown_asyncgens())
        loop.stop()
