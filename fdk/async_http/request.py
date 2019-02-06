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

from httptools import parse_url


logger = logging.getLogger(__name__)


DEFAULT_HTTP_CONTENT_TYPE = "application/octet-stream"


# HTTP/1.1: https://www.w3.org/Protocols/rfc2616/rfc2616-sec7.html#sec7.2.1
# > If the media type remains unknown, the recipient SHOULD treat it
# > as type "application/octet-stream"


class RequestParameters(dict):
    """Hosts a dict with lists as values where get returns the first
    value of the list and getlist returns the whole shebang
    """

    def get(self, name, default=None):
        """Return the first value, either the default or actual"""
        return super().get(name, [default])[0]

    def getlist(self, name, default=None):
        """Return the entire list"""
        return super().get(name, default)


class StreamBuffer(object):
    def __init__(self, buffer_size=100):
        self._queue = asyncio.Queue(buffer_size)

    async def read(self):
        """ Stop reading when gets None """
        payload = await self._queue.get()
        self._queue.task_done()
        return payload

    async def put(self, payload):
        await self._queue.put(payload)

    def is_full(self):
        return self._queue.full()


class Request(dict):
    """Properties of an HTTP request such as URL, headers, etc."""

    __slots__ = (
        "__weakref__",
        "_cookies",
        "_ip",
        "_parsed_url",
        "_port",
        "_remote_addr",
        "_socket",
        "app",
        "body",
        "endpoint",
        "headers",
        "method",
        "parsed_args",
        "parsed_files",
        "parsed_form",
        "parsed_json",
        "raw_url",
        "stream",
        "transport",
        "uri_template",
        "version",
    )

    def __init__(self, url_bytes, headers, version, method, transport):
        self.raw_url = url_bytes
        # TODO: Content-Encoding detection
        self._parsed_url = parse_url(url_bytes)
        self.app = None

        self.headers = headers
        self.version = version
        self.method = method
        self.transport = transport

        # Init but do not inhale
        self.body_init()
        self.parsed_json = None
        self.parsed_form = None
        self.parsed_files = None
        self.parsed_args = None
        self.uri_template = None
        self._cookies = None
        self.stream = None
        self.endpoint = None

    def __repr__(self):
        if self.method is None or not self.path:
            return "<{0}>".format(self.__class__.__name__)
        return "<{0}: {1} {2}>".format(
            self.__class__.__name__, self.method, self.path
        )

    def __bool__(self):
        if self.transport:
            return True
        return False

    def body_init(self):
        self.body = []

    def body_push(self, data):
        self.body.append(data)

    def body_finish(self):
        self.body = b"".join(self.body)

    @property
    def token(self):
        """Attempt to return the auth header token.

        :return: token related to request
        """
        prefixes = ("Bearer", "Token")
        auth_header = self.headers.get("Authorization")

        if auth_header is not None:
            for prefix in prefixes:
                if prefix in auth_header:
                    return auth_header.partition(prefix)[-1].strip()

        return auth_header

    @property
    def content_type(self):
        return self.headers.get("Content-Type", DEFAULT_HTTP_CONTENT_TYPE)


    @property
    def path(self):
        return self._parsed_url.path.decode("utf-8")

    @property
    def query_string(self):
        if self._parsed_url.query:
            return self._parsed_url.query.decode("utf-8")
        else:
            return ""
