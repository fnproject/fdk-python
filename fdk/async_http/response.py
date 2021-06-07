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

from functools import partial
from urllib.parse import quote_plus

from .exceptions import (
    STATUS_CODES, has_message_body, remove_entity_headers
)

from json import dumps


json_dumps = partial(dumps, separators=(",", ":"))


class BaseHTTPResponse(object):

    def _encode_body(self, data):
        try:
            # Try to encode it regularly
            return data.encode()
        except AttributeError:
            # Convert it to a str if you can't
            return str(data).encode()

    def _parse_headers(self):
        headers = b""
        for name, value in self.headers.items():
            try:
                headers += b"%b: %b\r\n" % (
                    name.encode(),
                    value.encode("utf-8"),
                )
            except AttributeError:
                headers += b"%b: %b\r\n" % (
                    str(name).encode(),
                    str(value).encode("utf-8"),
                )

        return headers


class StreamingHTTPResponse(BaseHTTPResponse):
    __slots__ = (
        "protocol",
        "streaming_fn",
        "status",
        "content_type",
        "headers",
        "_cookies",
    )

    def __init__(
        self, streaming_fn, status=200, headers=None, content_type="text/plain"
    ):
        self.content_type = content_type
        self.streaming_fn = streaming_fn
        self.status = status
        self.headers = dict(headers or {})
        self._cookies = None

    async def write(self, data):
        """Writes a chunk of data to the streaming response.

        :param data: bytes-ish data to be written.
        """
        if type(data) != bytes:
            data = self._encode_body(data)

        self.protocol.push_data(b"%x\r\n%b\r\n" % (len(data), data))
        await self.protocol.drain()

    async def stream(
        self, version="1.1", keep_alive=False, keep_alive_timeout=None
    ):
        """Streams headers, runs the `streaming_fn` callback that writes
        content to the response body, then finalizes the response body.
        """
        headers = self.get_headers(
            version,
            keep_alive=keep_alive,
            keep_alive_timeout=keep_alive_timeout,
        )
        self.protocol.push_data(headers)
        await self.protocol.drain()
        await self.streaming_fn(self)
        self.protocol.push_data(b"0\r\n\r\n")
        # no need to await drain here after this write, because it is the
        # very last thing we write and nothing needs to wait for it.

    def get_headers(
        self, version="1.1", keep_alive=False, keep_alive_timeout=None
    ):
        # This is all returned in a kind-of funky way
        # We tried to make this as fast as possible in pure python
        timeout_header = b""
        if keep_alive and keep_alive_timeout is not None:
            timeout_header = b"Keep-Alive: %d\r\n" % keep_alive_timeout

        self.headers["Transfer-Encoding"] = "chunked"
        self.headers.pop("Content-Length", None)
        self.headers["Content-Type"] = self.headers.get(
            "Content-Type", self.content_type
        )

        headers = self._parse_headers()

        if self.status == 200:
            status = b"OK"
        else:
            status = STATUS_CODES.get(self.status)

        return (b"HTTP/%b %d %b\r\n" b"%b" b"%b\r\n") % (
            version.encode(),
            self.status,
            status,
            timeout_header,
            headers,
        )


# CaseInsensitiveDict for headers. TODO should we let users use it in fdk too?
class CaseInsensitiveDict(dict):
    @classmethod
    def _k(cls, key):
        return key.lower() if isinstance(key, str) else key

    def __init__(self, *args, **kwargs):
        super(CaseInsensitiveDict, self).__init__(*args, **kwargs)
        self._convert_keys()

    def __getitem__(self, key):
        return super(CaseInsensitiveDict, self).__getitem__(
            self.__class__._k(key))

    def __setitem__(self, key, value):
        super(CaseInsensitiveDict, self).__setitem__(
            self.__class__._k(key), value)

    def __delitem__(self, key):
        return super(CaseInsensitiveDict, self).__delitem__(
            self.__class__._k(key))

    def __contains__(self, key):
        return super(CaseInsensitiveDict, self).__contains__(
            self.__class__._k(key))

    # DEPRECATED
    # def has_key(self, key):

    def pop(self, key, *args, **kwargs):
        return super(CaseInsensitiveDict, self).pop(
            self.__class__._k(key), *args, **kwargs)

    def get(self, key, *args, **kwargs):
        return super(CaseInsensitiveDict, self).get(
            self.__class__._k(key), *args, **kwargs)

    def setdefault(self, key, *args, **kwargs):
        return super(CaseInsensitiveDict, self).setdefault(
            self.__class__._k(key), *args, **kwargs)

    def update(self, E={}, **F):
        super(CaseInsensitiveDict, self).update(self.__class__(E))
        super(CaseInsensitiveDict, self).update(self.__class__(**F))

    def _convert_keys(self):
        for k in list(self.keys()):
            v = super(CaseInsensitiveDict, self).pop(k)
            self.__setitem__(k, v)


class HTTPResponse(BaseHTTPResponse):
    __slots__ = ("body", "status", "content_type", "headers", "_cookies")

    def __init__(
        self,
        body=None,
        status=200,
        headers=None,
        content_type="text/plain",
        body_bytes=b"",
    ):
        self.content_type = content_type

        if body is not None:
            self.body = self._encode_body(body)
        else:
            self.body = body_bytes

        self.status = status
        self.headers = CaseInsensitiveDict(headers or {})
        self._cookies = None

    def output(self, version="1.1", keep_alive=False, keep_alive_timeout=None):
        # This is all returned in a kind-of funky way
        # We tried to make this as fast as possible in pure python
        timeout_header = b""
        if keep_alive and keep_alive_timeout is not None:
            timeout_header = b"Keep-Alive: %d\r\n" % keep_alive_timeout

        body = b""
        if has_message_body(self.status):
            body = self.body
            self.headers["Content-Length"] = self.headers.get(
                "Content-Length", len(self.body)
            )

        self.headers["Content-Type"] = self.headers.get(
            "Content-Type", self.content_type
        )

        if self.status in (304, 412):
            self.headers = remove_entity_headers(self.headers)

        headers = self._parse_headers()

        if self.status == 200:
            status = b"OK"
        else:
            status = STATUS_CODES.get(self.status, b"UNKNOWN RESPONSE")

        return (
            b"HTTP/%b %d %b\r\n" b"Connection: %b\r\n" b"%b" b"%b\r\n" b"%b"
        ) % (
            version.encode(),
            self.status,
            status,
            b"keep-alive" if keep_alive else b"close",
            timeout_header,
            headers,
            body,
        )


def json(
    body,
    status=200,
    headers=None,
    content_type="application/json",
    dumps=json_dumps,
    **kwargs
):
    """
    Returns response object with body in json format.

    :param body: Response data to be serialized.
    :param status: Response code.
    :param headers: Custom Headers.
    :param kwargs: Remaining arguments that are passed to the json encoder.
    """
    return HTTPResponse(
        dumps(body, **kwargs),
        headers=headers,
        status=status,
        content_type=content_type,
    )


def text(
    body, status=200, headers=None, content_type="text/plain; charset=utf-8"
):
    """
    Returns response object with body in text format.

    :param body: Response data to be encoded.
    :param status: Response code.
    :param headers: Custom Headers.
    :param content_type: the content type (string) of the response
    """
    return HTTPResponse(
        body, status=status, headers=headers, content_type=content_type
    )


def raw(
    body, status=200, headers=None, content_type="application/octet-stream"
):
    """
    Returns response object without encoding the body.

    :param body: Response data.
    :param status: Response code.
    :param headers: Custom Headers.
    :param content_type: the content type (string) of the response.
    """
    return HTTPResponse(
        body_bytes=body,
        status=status,
        headers=headers,
        content_type=content_type,
    )


def html(body, status=200, headers=None):
    """
    Returns response object with body in html format.

    :param body: Response data to be encoded.
    :param status: Response code.
    :param headers: Custom Headers.
    """
    return HTTPResponse(
        body,
        status=status,
        headers=headers,
        content_type="text/html; charset=utf-8",
    )


def stream(
    streaming_fn,
    status=200,
    headers=None,
    content_type="text/plain; charset=utf-8",
):
    """Accepts an coroutine `streaming_fn` which can be used to
    write chunks to a streaming response. Returns a `StreamingHTTPResponse`.

    Example usage::

        @app.route("/")
        async def index(request):
            async def streaming_fn(response):
                await response.write('foo')
                await response.write('bar')

            return stream(streaming_fn, content_type='text/plain')

    :param streaming_fn: A coroutine accepts a response and
        writes content to that response.
    :param mime_type: Specific mime_type.
    :param headers: Custom Headers.
    """
    return StreamingHTTPResponse(
        streaming_fn, headers=headers, content_type=content_type, status=status
    )


def redirect(
    to, headers=None, status=302, content_type="text/html; charset=utf-8"
):
    """Abort execution and cause a 302 redirect (by default).

    :param to: path or fully qualified URL to redirect to
    :param headers: optional dict of headers to include in the new request
    :param status: status code (int) of the new request, defaults to 302
    :param content_type: the content type (string) of the response
    :returns: the redirecting Response
    """
    headers = headers or {}

    # URL Quote the URL before redirecting
    safe_to = quote_plus(to, safe=":/%#?&=@[]!$&'()*+,;")

    # According to RFC 7231, a relative URI is now permitted.
    headers["Location"] = safe_to

    return HTTPResponse(
        status=status, headers=headers, content_type=content_type
    )
