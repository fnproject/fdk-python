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
import sys

from .response import html, text

from traceback import extract_tb, format_exc

from .exceptions import (
    INTERNAL_SERVER_ERROR_HTML,
    TRACEBACK_BORDER,
    TRACEBACK_LINE_HTML,
    TRACEBACK_STYLE,
    TRACEBACK_WRAPPER_HTML,
    TRACEBACK_WRAPPER_INNER_HTML,
    AsyncHTTPException,
)

logger = logging.getLogger(__name__)


class ErrorHandler(object):
    handlers = None
    cached_handlers = None
    _missing = object()

    def __init__(self):
        self.handlers = []
        self.cached_handlers = {}
        self.debug = False

    def _render_exception(self, exception):
        frames = extract_tb(exception.__traceback__)

        frame_html = []
        for frame in frames:
            frame_html.append(TRACEBACK_LINE_HTML.format(frame))

        return TRACEBACK_WRAPPER_INNER_HTML.format(
            exc_name=exception.__class__.__name__,
            exc_value=exception,
            frame_html="".join(frame_html),
        )

    def _render_traceback_html(self, exception, request):
        exc_type, exc_value, tb = sys.exc_info()
        exceptions = []

        while exc_value:
            exceptions.append(self._render_exception(exc_value))
            exc_value = exc_value.__cause__

        return TRACEBACK_WRAPPER_HTML.format(
            style=TRACEBACK_STYLE,
            exc_name=exception.__class__.__name__,
            exc_value=exception,
            inner_html=TRACEBACK_BORDER.join(reversed(exceptions)),
            path=request.path,
        )

    def add(self, exception, handler):
        self.handlers.append((exception, handler))

    def lookup(self, exception):
        handler = self.cached_handlers.get(type(exception), self._missing)
        if handler is self._missing:
            for exception_class, handler in self.handlers:
                if isinstance(exception, exception_class):
                    self.cached_handlers[type(exception)] = handler
                    return handler
            self.cached_handlers[type(exception)] = None
            handler = None
        return handler

    def response(self, request, exception):
        """Fetches and executes an exception handler and returns a response
        object

        :param request: Request
        :param exception: Exception to handle
        :return: Response object
        """
        handler = self.lookup(exception)
        response = None
        try:
            if handler:
                response = handler(request, exception)
            if response is None:
                response = self.default(request, exception)
        except Exception:
            self.log(format_exc())
            try:
                url = repr(request.url)
            except AttributeError:
                url = "unknown"
            response_message = (
                "Exception raised in exception handler " '"%s" for uri: %s'
            )
            logger.exception(response_message, handler.__name__, url)

            if self.debug:
                return text(response_message % (handler.__name__, url), 500)
            else:
                return text("An error occurred while handling an error", 500)
        return response

    def default(self, request, exception):
        logger.error(format_exc())
        try:
            url = repr(request.url)
        except AttributeError:
            url = "unknown"

        response_message = ("Exception occurred while "
                            "handling uri: {0}".format(url))
        logger.error(response_message, exc_info=1)

        if issubclass(type(exception), AsyncHTTPException):
            return text(
                "Error: {}".format(exception),
                status=getattr(exception, "status_code", 500),
                headers=getattr(exception, "headers", dict()),
            )
        elif self.debug:
            html_output = self._render_traceback_html(exception, request)

            return html(html_output, status=500)
        else:
            return html(INTERNAL_SERVER_ERROR_HTML, status=500)
