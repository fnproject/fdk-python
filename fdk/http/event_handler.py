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
import h11

from fdk import constants
from fdk import customer_code
from fdk import log
from fdk import runner

from fdk.http import routine


def event_handle(handle_code: customer_code.Function):
    """
    Performs HTTP request-response procedure
    :param handle_code: customer's code
    :type handle_code: fdk.customer_code.Function
    :return: None
    """
    async def pure_handler(request_reader: asyncio.StreamReader,
                           response_writer: asyncio.StreamWriter):
        log.log("in pure_handler")
        connection = h11.Connection(h11.SERVER)
        try:
            log.log("server state: {0}".format(connection.our_state))
            request, body = await routine.read_request(
                connection, request_reader)
            func_response = await runner.handle_request(
                handle_code, constants.HTTPSTREAM,
                headers=dict(request.headers), data=body)
            log.log("request execution completed")
            await routine.write_response(
                connection, func_response, response_writer)
        except Exception as ex:
            await routine.write_error(ex, connection, response_writer)
        finally:
            await response_writer.drain()
            await routine.maybe_close(connection, response_writer)

    return pure_handler
