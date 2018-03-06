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

import os
import sys
import ujson

from fdk import context
from fdk import errors
from fdk import headers


def readline(stream):
    """
    Read a line up until line can be valid JSON
    :param stream: input stream
    :type stream: io.TextIOWrapper[str]
    :return raw request body
    :rtype: dict
    """
    line = str()
    ret = False

    while True:
        c = stream.read(1)
        if c is None:
            continue
        if len(c) == 0:
            s = line.replace('\n"\n,', '",').replace("\n}", "}")
            print("Before JSON parsing: {}".format(s),
                  file=sys.stderr, flush=True)
            return ujson.loads(s) if len(s) > 0 else {}
        if c == "\n":
            line += c
            ret = True
        elif c == "}" and ret:
            line += c
            s = line.replace('\n"\n,', '",').replace("\n}", "}")
            # due to weird padding we omit last 4 bytes: \n}\n\n
            stream.read(4)
            s += "}"
            print("Before JSON parsing: {}".format(s),
                  file=sys.stderr, flush=True)
            return ujson.loads(s)
        else:
            ret = False
            line += c


class RawRequest(object):

    def __init__(self, stream):
        """
        Raw JSON request body constructor
        :param stream: byte stream
        :type stream: io.TextIOWrapper[str]
        """
        self.stream = stream
        self.body_stream = None

    def parse_raw_request(self):
        """
        Parses raw JSON request into its context and body
        :return: tuple of request context and body
        :rtype: tuple
        """
        if self.stream is None:
            raise EOFError("Previous stream had no terminator")
        try:
            incoming_json = readline(self.stream)
            print("After JSON parsing: {}".format(incoming_json),
                  file=sys.stderr, flush=True)
            json_headers = headers.GoLikeHeaders(
                incoming_json.get('protocol', {"headers": {}}).get("headers"))
            ctx = context.JSONContext(os.environ.get("FN_APP_NAME"),
                                      os.environ.get("FN_PATH"),
                                      incoming_json.get("call_id"),
                                      execution_type=incoming_json.get(
                                          "type", "sync"),
                                      deadline=incoming_json.get("deadline"),
                                      config=os.environ, headers=json_headers)
            return ctx, incoming_json.get('body')
        except Exception as ex:
            print("Error while parsing JSON: {}".format(str(ex)),
                  file=sys.stderr, flush=True)
            ctx = context.JSONContext(
                os.environ.get("FN_APP_NAME"),
                os.environ.get("FN_PATH"), "",
            )
            raise errors.JSONDispatchException(ctx, 500, str(ex))
