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

import httptools

MAX_RECV = 2 ** 16 # Byte
TIMEOUT = 10 # Second

# NOTE: we do not need pipelining or ASGI
# TODO(reed): figure out how to get an HTTPProtocol that has handle_code in it
# TODO(reed): handle streaming
# TODO(reed): handle 100 continue
# TODO(reed): handle keep alives is done-ish? ensure
# TODO(reed): handle errors

class HttpRequest:
    __slots__ = ('_protocol', '_url', '_headers', '_version')

    def __init__(self, protocol, url, headers, version):
        self._protocol = protocol
        self._url = url
        self._headers = headers
        self._version = version


class HttpResponse:
    __slots__ = ('_protocol', '_request', '_headers_sent')

    def __init__(self, protocol, request):
        self._protocol = protocol
        self._request = request
        self._headers_sent = False

    def write(self, data):
        self._protocol._transport.write(b''.join([
            'HTTP/{} 200 OK\r\n'.format(
                self._request._version).encode('latin-1'),
            b'Content-Type: text/plain\r\n',
            'Content-Length: {}\r\n'.format(len(data)).encode('latin-1'),
            b'\r\n',
            data
        ]))

class HTTPProtocol(asyncio.Protocol):

    __slots__ = ('_loop',
                 '_transport', '_current_request', '_current_parser',
                 '_current_url', '_current_headers')

    def __init__(self, *, loop=None):
        if loop is None:
            loop = asyncio.get_event_loop()
        self._loop = loop
        self._transport = None
        self._current_request = None
        self._current_parser = None
        self._current_url = None
        self._current_headers = None

    def on_url(self, url):
        self._current_url = url

    def on_header(self, name, value):
        self._current_headers.append((name, value))

    def on_headers_complete(self):
        self._current_request = HttpRequest(
            self, self._current_url, self._current_headers,
            self._current_parser.get_http_version())

        self._loop.call_soon(
            self.handle, self._current_request,
            HttpResponse(self, self._current_request))

    ####

    def connection_made(self, transport):
        self._transport = transport

    def connection_lost(self, exc):
        self._current_request = self._current_parser = None

    def data_received(self, data):
        if self._current_parser is None:
            assert self._current_request is None
            self._current_headers = []
            self._current_parser = httptools.HttpRequestParser(self)

        self._current_parser.feed_data(data)

    def handle(self, request, response):
        parsed_url = httptools.parse_url(self._current_url)
        resp = b'hello world'
        response.write(resp)
        if not self._current_parser.should_keep_alive():
            self._transport.close()
        self._current_parser = None
        self._current_request = None


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

    loop = asyncio.get_event_loop()
    server = loop.run_until_complete(loop.create_unix_server(HTTPProtocol, path=phony_socket_path))

    try:
        log.log("CHMOD 666 {0}".format(phony_socket_path))
        os.chmod(phony_socket_path, 0o666)
        log.log("phony socket permissions: {0}"
                .format(oct(os.stat(phony_socket_path).st_mode)))
        log.log("calling '.start_serving()'")
        # start_serving()
        log.log("sym-linking {0} to {1}".format(
            socket_path, phony_socket_path))
        os.symlink(os.path.basename(phony_socket_path), socket_path)
        log.log("socket permissions: {0}"
                .format(oct(os.stat(socket_path).st_mode)))
        log.log("starting infinite loop")

    except (Exception, BaseException) as ex:
        log.log(str(ex))
        raise ex

    loop.run_until_complete(server.serve_forever())


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
