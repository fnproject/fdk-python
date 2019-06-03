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
import logging
import os

from inspect import isawaitable
from time import time

from functools import partial
from signal import SIG_IGN, SIGINT, SIGTERM
from signal import signal as signal_func

from .protocol import HttpProtocol

from fdk import constants


class Signal(object):
    stopped = False


logger = logging.getLogger(__name__)


def update_current_time(loop):
    """Cache the current time, since it is needed at the end of every
    keep-alive request to update the request timeout time

    :param loop:
    :return:
    """
    global current_time
    current_time = time()
    loop.call_later(1, partial(update_current_time, loop))


def trigger_events(events, loop):
    """Trigger event callbacks (functions or async)

    :param events: one or more sync or async functions to execute
    :param loop: event loop
    """
    for event in events:
        result = event(loop)
        if isawaitable(result):
            loop.run_until_complete(result)


def serve(
    request_handler,
    error_handler,
    debug=False,
    request_timeout=60,
    response_timeout=60,
    keep_alive_timeout=75,
    ssl=None,
    sock=None,
    request_max_size=100000000,
    reuse_port=False,
    loop=None,
    protocol=HttpProtocol,
    backlog=100,
    register_sys_signals=True,
    run_multiple=False,
    run_async=False,
    connections=None,
    signal=Signal(),
    request_class=None,
    access_log=True,
    keep_alive=True,
    is_request_stream=False,
    router=None,
    websocket_max_size=None,
    websocket_max_queue=None,
    websocket_read_limit=2 ** 16,
    websocket_write_limit=2 ** 16,
    state=None,
):
    """Start asynchronous HTTP Server on an individual process.

    :param request_handler: Sanic request handler with middleware
    :param error_handler: Sanic error handler with middleware
    :param debug: enables debug output (slows server)
    :param request_timeout: time in seconds
    :param response_timeout: time in seconds
    :param keep_alive_timeout: time in seconds
    :param ssl: SSLContext
    :param sock: Socket for the server to accept connections from
    :param request_max_size: size in bytes, `None` for no limit
    :param reuse_port: `True` for multiple workers
    :param loop: asyncio compatible event loop
    :param protocol: subclass of asyncio protocol class
    :param request_class: Request class to use
    :param access_log: disable/enable access log
    :param websocket_max_size: enforces the maximum size for
                               incoming messages in bytes.
    :param websocket_max_queue: sets the maximum length of the queue
                                that holds incoming messages.
    :param websocket_read_limit: sets the high-water limit of the buffer for
                                 incoming bytes, the low-water limit is half
                                 the high-water limit.
    :param websocket_write_limit: sets the high-water limit of the buffer for
                                  outgoing bytes, the low-water limit is a
                                  quarter of the high-water limit.
    :param is_request_stream: disable/enable Request.stream
    :return: Nothing
    """
    if not run_async:
        # create new event_loop after fork
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if debug:
        loop.set_debug(debug)

    connections = connections if connections is not None else set()
    server = partial(
        protocol,
        loop=loop,
        connections=connections,
        signal=signal,
        request_handler=request_handler,
        error_handler=error_handler,
        request_timeout=request_timeout,
        response_timeout=response_timeout,
        keep_alive_timeout=keep_alive_timeout,
        request_max_size=request_max_size,
        request_class=request_class,
        access_log=access_log,
        keep_alive=keep_alive,
        is_request_stream=is_request_stream,
        router=router,
        websocket_max_size=websocket_max_size,
        websocket_max_queue=websocket_max_queue,
        websocket_read_limit=websocket_read_limit,
        websocket_write_limit=websocket_write_limit,
        state=state,
        debug=debug,
    )

    create_server_kwargs = dict(
        ssl=ssl,
        reuse_port=reuse_port,
        sock=sock,
        backlog=backlog,
    )

    if constants.is_py37():
        create_server_kwargs.update(
            start_serving=False
        )

    server_coroutine = loop.create_server(
        server, **create_server_kwargs
    )

    # Instead of pulling time at the end of every request,
    # pull it once per minute
    loop.call_soon(partial(update_current_time, loop))

    if run_async:
        return server_coroutine

    try:
        http_server = loop.run_until_complete(server_coroutine)
    except BaseException:
        logger.exception("Unable to start server")
        return

    # Ignore SIGINT when run_multiple
    if run_multiple:
        signal_func(SIGINT, SIG_IGN)

    # Register signals for graceful termination
    if register_sys_signals:
        _signals = (SIGTERM,) if run_multiple else (SIGINT, SIGTERM)
        for _signal in _signals:
            try:
                loop.add_signal_handler(_signal, loop.stop)
            except NotImplementedError:
                logger.warning(
                    "Sanic tried to use loop.add_signal_handler "
                    "but it is not implemented on this platform."
                )

    def start_serving():
        if constants.is_py37():
            loop.run_until_complete(http_server.start_serving())

    def start():
        pid = os.getpid()
        try:
            logger.info("Starting worker [%s]", pid)
            if constants.is_py37():
                loop.run_until_complete(http_server.serve_forever())
            else:
                loop.run_forever()
        finally:
            http_server.close()
            loop.run_until_complete(http_server.wait_closed())
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()

    return start_serving, start
