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

"""Defines basics of HTTP standard."""

# TODO: use native python tools to build this map at the runtime
STATUS_CODES = {
    100: b"Continue",
    101: b"Switching Protocols",
    102: b"Processing",
    200: b"OK",
    201: b"Created",
    202: b"Accepted",
    203: b"Non-Authoritative Information",
    204: b"No Content",
    205: b"Reset Content",
    206: b"Partial Content",
    207: b"Multi-Status",
    208: b"Already Reported",
    226: b"IM Used",
    300: b"Multiple Choices",
    301: b"Moved Permanently",
    302: b"Found",
    303: b"See Other",
    304: b"Not Modified",
    305: b"Use Proxy",
    307: b"Temporary Redirect",
    308: b"Permanent Redirect",
    400: b"Bad Request",
    401: b"Unauthorized",
    402: b"Payment Required",
    403: b"Forbidden",
    404: b"Not Found",
    405: b"Method Not Allowed",
    406: b"Not Acceptable",
    407: b"Proxy Authentication Required",
    408: b"Request Timeout",
    409: b"Conflict",
    410: b"Gone",
    411: b"Length Required",
    412: b"Precondition Failed",
    413: b"Request Entity Too Large",
    414: b"Request-URI Too Long",
    415: b"Unsupported Media Type",
    416: b"Requested Range Not Satisfiable",
    417: b"Expectation Failed",
    418: b"I'm a teapot",
    422: b"Unprocessable Entity",
    423: b"Locked",
    424: b"Failed Dependency",
    426: b"Upgrade Required",
    428: b"Precondition Required",
    429: b"Too Many Requests",
    431: b"Request Header Fields Too Large",
    451: b"Unavailable For Legal Reasons",
    500: b"Internal Server Error",
    501: b"Not Implemented",
    502: b"Bad Gateway",
    503: b"Service Unavailable",
    504: b"Gateway Timeout",
    505: b"HTTP Version Not Supported",
    506: b"Variant Also Negotiates",
    507: b"Insufficient Storage",
    508: b"Loop Detected",
    510: b"Not Extended",
    511: b"Network Authentication Required",
}

# According to https://tools.ietf.org/html/rfc2616#section-7.1
_ENTITY_HEADERS = frozenset(
    [
        "allow",
        "content-encoding",
        "content-language",
        "content-length",
        "content-location",
        "content-md5",
        "content-range",
        "content-type",
        "expires",
        "last-modified",
        "extension-header",
    ]
)

# According to https://tools.ietf.org/html/rfc2616#section-13.5.1
_HOP_BY_HOP_HEADERS = frozenset(
    [
        "connection",
        "keep-alive",
        "proxy-authenticate",
        "proxy-authorization",
        "te",
        "trailers",
        "transfer-encoding",
        "upgrade",
    ]
)


def has_message_body(status):
    """
    According to the following RFC message body and length SHOULD NOT
    be included in responses status 1XX, 204 and 304.
    https://tools.ietf.org/html/rfc2616#section-4.4
    https://tools.ietf.org/html/rfc2616#section-4.3
    """
    return status not in (204, 304) and not (100 <= status < 200)


def is_entity_header(header):
    """Checks if the given header is an Entity Header"""
    return header.lower() in _ENTITY_HEADERS


def is_hop_by_hop_header(header):
    """Checks if the given header is a Hop By Hop header"""
    return header.lower() in _HOP_BY_HOP_HEADERS


def remove_entity_headers(headers, allowed=("content-location", "expires")):
    """
    Removes all the entity headers present in the headers given.
    According to RFC 2616 Section 10.3.5,
    Content-Location and Expires are allowed as for the
    "strong cache validator".
    https://tools.ietf.org/html/rfc2616#section-10.3.5

    returns the headers without the entity headers
    """
    allowed = set([h.lower() for h in allowed])
    headers = {
        header: value
        for header, value in headers.items()
        if not is_entity_header(header) or header.lower() in allowed
    }
    return headers


TRACEBACK_STYLE = """
    <style>
        body {
            padding: 20px;
            font-family: Arial, sans-serif;
        }

        p {
            margin: 0;
        }

        .summary {
            padding: 10px;
        }

        h1 {
            margin-bottom: 0;
        }

        h3 {
            margin-top: 10px;
        }

        h3 code {
            font-size: 24px;
        }

        .frame-line > * {
            padding: 5px 10px;
        }

        .frame-line {
            margin-bottom: 5px;
        }

        .frame-code {
            font-size: 16px;
            padding-left: 30px;
        }

        .tb-wrapper {
            border: 1px solid #f3f3f3;
        }

        .tb-header {
            background-color: #f3f3f3;
            padding: 5px 10px;
        }

        .tb-border {
            padding-top: 20px;
        }

        .frame-descriptor {
            background-color: #e2eafb;
        }

        .frame-descriptor {
            font-size: 14px;
        }
    </style>
"""

TRACEBACK_WRAPPER_HTML = """
    <html>
        <head>
            {style}
        </head>
        <body>
            {inner_html}
            <div class="summary">
                <p>
                <b>{exc_name}: {exc_value}</b>
                    while handling path <code>{path}</code>
                </p>
            </div>
        </body>
    </html>
"""

TRACEBACK_WRAPPER_INNER_HTML = """
    <h1>{exc_name}</h1>
    <h3><code>{exc_value}</code></h3>
    <div class="tb-wrapper">
        <p class="tb-header">Traceback (most recent call last):</p>
        {frame_html}
    </div>
"""

TRACEBACK_BORDER = """
    <div class="tb-border">
        <b><i>
            The above exception was the direct cause of the
            following exception:
        </i></b>
    </div>
"""

TRACEBACK_LINE_HTML = """
    <div class="frame-line">
        <p class="frame-descriptor">
            File {0.filename}, line <i>{0.lineno}</i>,
            in <code><b>{0.name}</b></code>
        </p>
        <p class="frame-code"><code>{0.line}</code></p>
    </div>
"""

INTERNAL_SERVER_ERROR_HTML = """
    <h1>Internal Server Error</h1>
    <p>
        The server encountered an internal error and cannot complete
        your request.
    </p>
"""


_excs = {}


def add_status_code(code):
    """
    Decorator used for adding exceptions to _sanic_exceptions.
    """

    def class_decorator(cls):
        cls.status_code = code
        _excs[code] = cls
        return cls

    return class_decorator


class AsyncHTTPException(Exception):
    def __init__(self, message, status_code=None):
        super().__init__(message)

        if status_code is not None:
            self.status_code = status_code


@add_status_code(404)
class NotFound(AsyncHTTPException):
    pass


@add_status_code(400)
class InvalidUsage(AsyncHTTPException):
    pass


@add_status_code(405)
class MethodNotSupported(AsyncHTTPException):
    def __init__(self, message, method, allowed_methods):
        super().__init__(message)
        self.headers = dict()
        self.headers["Allow"] = ", ".join(allowed_methods)
        if method in ["HEAD", "PATCH", "PUT", "DELETE"]:
            self.headers["Content-Length"] = 0


@add_status_code(500)
class ServerError(AsyncHTTPException):
    pass


@add_status_code(503)
class ServiceUnavailable(AsyncHTTPException):
    """The server is currently unavailable (because it is overloaded or
    down for maintenance). Generally, this is a temporary state."""

    pass


class URLBuildError(ServerError):
    pass


class FileNotFound(NotFound):
    def __init__(self, message, path, relative_url):
        super().__init__(message)
        self.path = path
        self.relative_url = relative_url


@add_status_code(408)
class RequestTimeout(AsyncHTTPException):
    """The Web server (running the Web site) thinks that there has been too
    long an interval of time between 1) the establishment of an IP
    connection (socket) between the client and the server and
    2) the receipt of any data on that socket, so the server has dropped
    the connection. The socket connection has actually been lost - the Web
    server has 'timed out' on that particular socket connection.
    """

    pass


@add_status_code(413)
class PayloadTooLarge(AsyncHTTPException):
    pass


class HeaderNotFound(InvalidUsage):
    pass


@add_status_code(416)
class ContentRangeError(AsyncHTTPException):
    def __init__(self, message, content_range):
        super().__init__(message)
        self.headers = {
            "Content-Type": "text/plain",
            "Content-Range": "bytes */%s" % (content_range.total,),
        }


@add_status_code(403)
class Forbidden(AsyncHTTPException):
    pass


class InvalidRangeType(ContentRangeError):
    pass


class PyFileError(Exception):
    def __init__(self, file):
        super().__init__("could not execute config file %s", file)


@add_status_code(401)
class Unauthorized(AsyncHTTPException):
    """
    Unauthorized exception (401 HTTP status code).

    :param message: Message describing the exception.
    :param status_code: HTTP Status code.
    :param scheme: Name of the authentication scheme to be used.

    When present, kwargs is used to complete the WWW-Authentication header.

    Examples::

        # With a Basic auth-scheme, realm MUST be present:
        raise Unauthorized("Auth required.",
                           scheme="Basic",
                           realm="Restricted Area")

        # With a Digest auth-scheme, things are a bit more complicated:
        raise Unauthorized("Auth required.",
                           scheme="Digest",
                           realm="Restricted Area",
                           qop="auth, auth-int",
                           algorithm="MD5",
                           nonce="abcdef",
                           opaque="zyxwvu")

        # With a Bearer auth-scheme, realm is optional so you can write:
        raise Unauthorized("Auth required.", scheme="Bearer")

        # or, if you want to specify the realm:
        raise Unauthorized("Auth required.",
                           scheme="Bearer",
                           realm="Restricted Area")
    """

    def __init__(self, message, status_code=None, scheme=None, **kwargs):
        super().__init__(message, status_code)

        # if auth-scheme is specified, set "WWW-Authenticate" header
        if scheme is not None:
            values = ['{!s}="{!s}"'.format(k, v) for k, v in kwargs.items()]
            challenge = ", ".join(values)

            self.headers = {
                "WWW-Authenticate": "{} {}".format(scheme, challenge).rstrip()
            }


def abort(status_code, message=None):
    """
    Raise an exception based on AsyncHTTPException. Returns the HTTP response
    message appropriate for the given status code, unless provided.

    :param status_code: The HTTP status code to return.
    :param message: The HTTP response body. Defaults to the messages
                    in response.py for the given status code.
    """
    if message is None:
        message = STATUS_CODES.get(status_code)
        # These are stored as bytes in the STATUS_CODES dict
        message = message.decode("utf8")
    exc = _excs.get(status_code, AsyncHTTPException)
    raise exc(message=message, status_code=status_code)
