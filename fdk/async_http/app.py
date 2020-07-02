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

import logging

from asyncio import CancelledError
from traceback import format_exc

from .exceptions import AsyncHTTPException
from .error_handler import ErrorHandler
from .request import Request
from .response import HTTPResponse, StreamingHTTPResponse
from .server import serve

logger = logging.getLogger(__name__)


class AsyncHTTPServer(object):
    def __init__(
        self,
        name=None,
        router=None,
    ):

        self.name = name
        self.router = router
        self.request_class = Request
        self.error_handler = ErrorHandler()
        self.config = {}
        self.debug = None
        self.sock = None
        self.is_running = False
        self.is_request_stream = False
        self.websocket_enabled = False
        self.websocket_tasks = set()

        # Register alternative method names
        self.go_fast = self.run

    async def handle_request(self, request, write_callback, stream_callback):
        """Take a request from the HTTP Server and return a response object
        to be sent back The HTTP Server only expects a response object, so
        exception handling must be done here
        :param request: HTTP Request object
        :param write_callback: Synchronous response function to be
            called with the response as the only argument
        :param stream_callback: Coroutine that handles streaming a
            StreamingHTTPResponse if produced by the handler.
        :return: Nothing
        """
        # Define `response` var here to remove warnings about
        # allocation before assignment below.
        cancelled = False
        try:
            request.app = self
            # -------------------------------------------- #
            # Execute Handler
            # -------------------------------------------- #

            # Fetch handler from router
            handler, uri = self.router.get(
                request.path, request.method)

            request.uri_template = uri
            response = handler(request)
            logger.info("got response from function")
            res = await response
            body = res.body
            headers = res.headers
            status = res.status
            response = HTTPResponse(
                body_bytes=body, status=status, headers=headers,
            )
        except CancelledError:
            response = None
            cancelled = True
        except Exception as e:
            if isinstance(e, AsyncHTTPException):
                response = self.error_handler.default(
                    request=request, exception=e
                )
            elif self.debug:
                response = HTTPResponse(
                    "Error while handling error: {}\nStack: {}".format(
                        e, format_exc()
                    ),
                    status=502,
                )
            else:
                response = HTTPResponse(
                    "An error occurred while handling an error", status=502
                )
        finally:
            if cancelled:
                raise CancelledError()

        if isinstance(response, StreamingHTTPResponse):
            await stream_callback(response)
        else:
            write_callback(response)

    def run(self, sock=None, loop=None):
        return serve(
            self.handle_request, ErrorHandler(),
            sock=sock, loop=loop
        )
