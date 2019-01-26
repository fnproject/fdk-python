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
import socket
import sys

from fdk import constants
from fdk import customer_code
from fdk import log

MAX_RECV = 2 ** 16 # Byte
TIMEOUT = 10 # Second

# NOTE: we do not need pipelining or ASGI
# TODO(reed): figure out how to get an HTTPProtocol that has handle_code in it
# TODO(reed): handle streaming
# TODO(reed): handle 100 continue
# TODO(reed): handle keep alives is done-ish? ensure
# TODO(reed): handle errors

class HTTPProtocol(asyncio.Protocol):

    def __init__(self):
        self.connection = h11.Connection(h11.SERVER)
        # handle timeouts
        loop = asyncio.get_running_loop()
        self.timeout_handle = loop.call_later(TIMEOUT, self._timeout)
        # flow control
        self._can_write = asyncio.Event()
        self._can_write.set()

    def connection_made(self, transport):
        self.transport = transport

    def connection_lost(self, error: Optional[Exception]):
        if error is not None:
            self.connection.send_failed()  # Set our state to error, prevents recycling

    def eof_received(self):
        self.data_received(b"")
        self._deliver_events()
        return True

    def data_received(self, data):
        self.connection.receive_data(data)
        self._deliver_events()

    # Internal helper function -- deliver all pending events
    def _deliver_events(self):
        self.timeout_handle.cancel() # stop keep alive timeout
        while True:
            event = self.connection.next_event()
            if isinstance(event, h11.Request):
                self.handle_request(event)
            elif event is h11.PAUSED:
                self.transport.pause_reading() # back pressure
                break
            elif (
                isinstance(event, h11.ConnectionClosed)
                or event is h11.NEED_DATA
            ):
                break

        if self.connection.our_state in {h11.ERROR, h11.MUST_CLOSE}:
            self.close()
        else: # TODO(reed): check h11.DONE?
            self.start_next_cycle()
            self.timeout_handle = loop.call_later(TIMEOUT, self._timeout) # TODO(reed): extract function

    # Called by your code when its ready to start a new
    # request/response cycle
    def start_next_cycle(self):
        self.connection.start_next_cycle()
        # New events might have been buffered internally, and only
        # become deliverable after calling start_next_cycle
        self._deliver_events()
        # Remove back-pressure
        self.transport.resume_reading()

    # TODO async?
    def handle_request(self, request):
        # TODO(reed): if we want to be pedantic we could check POST /call

        # TODO(reed): handle code
        # logger.info("running user code")
        # func_response = await runner.handle_request(
            # handle_code, constants.HTTPSTREAM,
            # headers=dict(request.headers), data=io.BytesIO(request.body))
        # logger.info("user code execution completed")

        # TODO we need to gather the body in deliver events for flow control?
        data = b""
        while True:
            event = self.connection.next_event()
            if type(event) is h11.EndOfMessage:
                break
            assert type(event) is h11.Data
            data += event.data # TODO(reed): decode?

        body = b"%s %s %s" % (event.method.upper(), event.target, data)
        headers = [
            ('content-type', 'text/plain'),
            ('content-length', str(len(body))),
        ]
        response = h11.Response(status_code=200, headers=headers)
        self.send(response)
        self.send(h11.Data(data=body))
        self.send(h11.EndOfMessage())

    def send(self, event):
        data = self.connection.send(event)
        self.transport.write(data)

    def _timeout(self):
        self.close()

    def close(self):
        self.transport.close()
        self.resume_writing()
        self.timeout_handle.cancel() # stop keep alive timeout

    # flow control methods
    def pause_writing(self):
        # Will be called whenever the transport crosses the
        # high-water mark.
        self._can_write.clear()

    def resume_writing(self):
        # Will be called whenever the transport drops back below the
        # low-water mark.
        self._can_write.set()

    async def drain(self):
        await self._can_write.wait()


def start(handle_code: customer_code.Function,
          uds: str,
          loop: asyncio.AbstractEventLoop=None):
    """
    Unix domain socket HTTP server entry point
    :param handle_code: customer's code
    :type handle_code: fdk.customer_code.Function
    :param uds: path to a Unix domain socket
    :type uds: str
    :param loop: event loop
    :type loop: asyncio.AbstractEventLoop
    :return: None
    """
    log.log("in http_stream.start")
    socket_path = os.path.normpath(str(uds).lstrip("unix:"))
    socket_dir, socket_file = os.path.split(socket_path)
    if socket_file == "":
        sys.exit("malformed FN_LISTENER env var "
                 "value: {0}".format(socket_path))

    phony_socket_path = os.path.join(
        socket_dir, "phony" + socket_file)

    log.log("deleting socket files if they exist")
    try:
        os.remove(socket_path)
        os.remove(phony_socket_path)
    except OSError:
        pass

    loop = asyncio.get_running_loop()
    server = await loop.create_unix_server(HTTPProtocol, path=phony_socket_path)

    try:
        log.log("CHMOD 666 {0}".format(phony_socket_path))
        os.chmod(phony_socket_path, 0o666)
        log.log("phony socket permissions: {0}"
                .format(oct(os.stat(phony_socket_path).st_mode)))
        log.log("calling '.start_serving()'")
        start_serving()
        log.log("sym-linking {0} to {1}".format(
            socket_path, phony_socket_path))
        os.symlink(os.path.basename(phony_socket_path), socket_path)
        log.log("socket permissions: {0}"
                .format(oct(os.stat(socket_path).st_mode)))
        log.log("starting infinite loop")

    except (Exception, BaseException) as ex:
        log.log(str(ex))
        raise ex

    await server.serve_forever()


def handle(handle_code: customer_code.Function):
    """
    FDK entry point
    :param handle_code: customer's code
    :type handle_code: fdk.customer_code.Function
    :return: None
    """
    log.log("entering handle")
    if not isinstance(handle_code, customer_code.Function):
        sys.exit(
            '\n\n\nWARNING!\n\n'
            'Your code is not compatible the the latest FDK!\n\n'
            'Update Dockerfile entry point to:\n'
            'ENTRYPOINT["/python/bin/fdk", "<path-to-your-func.py>", {0}]\n\n'
            'if __name__ == "__main__":\n\tfdk.handle(handler)\n\n'
            'syntax no longer supported!\n'
            'Update your code as soon as possible!'
            '\n\n\n'.format(handle_code.__name__))

    loop = asyncio.get_event_loop()

    format_def = os.environ.get(constants.FN_FORMAT)
    lsnr = os.environ.get(constants.FN_LISTENER)
    log.log("{0} is set, value: {1}".
            format(constants.FN_FORMAT, format_def))

    if lsnr is None:
        sys.exit("{0} is not set".format(constants.FN_LISTENER))

    log.log("{0} is set, value: {1}".
            format(constants.FN_LISTENER, lsnr))

    if format_def == constants.HTTPSTREAM:
        start(handle_code, lsnr, loop=loop)
    else:
        sys.exit("incompatible function format!")
