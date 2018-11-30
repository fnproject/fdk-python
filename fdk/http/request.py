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

from fdk import constants
from fdk.http import parser
from fdk.http import streams

from urllib import parse


def parse_query_params(url):
    """
    Parses query parameters
    :param url: request URL
    :type url: str
    :return:
    """
    q = url.split('?')
    if len(q) < 2:
        return {}
    return parse.parse_qs(q[1], keep_blank_values=True)


class RawRequest(object):

    def __init__(self, stream):
        """
        Raw request constructor
        :param stream: byte stream
        :type stream: io.BytesIO[bytes]
        """
        self.stream = stream
        self.body_stream = None

    async def parse_raw_request(self):
        """Parses raw HTTP request that contains:
         - method
         - route + query
         - headers
         - protocol version
         Optionally:
         - data stream
         Raw HTTP request may have next look:
            GET /v1/apps?something=something&etc=etc HTTP/1.1
            Host: localhost:8080
            Content-Length: 5
            Content-Type: application/x-www-form-urlencoded
            User-Agent: curl/7.51.0
            hello
        Each new line define by set of special characters:
            \n
            \r
        and combination is:
            \r\n
        :return: tuple of HTTP method, HTTP URL, HTTP query parameters,
        HTTP headers, HTTP proto version, HTTP raw data
        :rtype: tuple
        """

        if self.body_stream is not None:
            # Consume any of the remainder of a previous request
            await self.body_stream.close()

        if self.stream is None:
            # We received a request that was incorrectly framed,
            # so had to consume all remaining input
            raise EOFError("Previous stream had no terminator")

        try:
            top_line = await parser.readline(self.stream)
            if len(top_line) == 0:
                raise EOFError("No request supplied")
            method, path, proto = top_line.rstrip().split(' ')
            headers = {}
            while True:
                line = await parser.readline(self.stream)
                line = line.rstrip()
                if len(line) == 0:
                    break
                k, v = line.split(':', 1)
                if k in headers:
                    headers[k] += ';' + v.strip()
                else:
                    headers[k] = v.strip()

            major_minor = proto.upper().replace("HTTP/", "").split(".")
            if len(major_minor) > 1:
                major, minor = major_minor
            else:
                major, minor = major_minor.pop(), "0"

            params = parse_query_params(path)

            if constants.CONTENT_LENGTH in headers:
                self.body_stream = streams.ContentLengthStream(
                    self.stream, int(headers.get(constants.CONTENT_LENGTH)))
            else:
                self.body_stream = streams.ChunkedStream(self.stream)
                self.stream = None

            return ((major, minor), path, method,
                    params, headers, self.body_stream)
        except ValueError:
            raise Exception("No request supplied")
