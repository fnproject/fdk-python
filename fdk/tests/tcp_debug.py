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

import asyncio
import socket

from fdk import customer_code
from fdk import event_handler
from fdk import log

from fdk.async_http import app
from fdk.async_http import router


def handle(handle_code: customer_code.Function, port: int = 5000):
    """
    FDK entry point
    :param handle_code: customer's code
    :type handle_code: fdk.customer_code.Function
    :param port: TCP port to start an FDK at
    :type port: int
    :return: None
    """
    host = "localhost"
    log.log("entering handle")

    log.log("Starting HTTP server on "
            "TCP socket: {0}:{1}".format(host, port))
    loop = asyncio.get_event_loop()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("localhost", port))

    rtr = router.Router()
    rtr.add("/call", frozenset({"POST"}),
            event_handler.event_handle(handle_code))
    srv = app.AsyncHTTPServer(name="fdk-tcp-debug", router=rtr)
    start_serving, server_forever = srv.run(sock=sock, loop=loop)
    start_serving()
    server_forever()
