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

import io

import testtools

from fdk.http import request
from fdk.tests import data


class TestHTTPRequestParser(testtools.TestCase):

    def setUp(self):
        super(TestHTTPRequestParser, self).setUp()

    def tearDown(self):
        super(TestHTTPRequestParser, self).tearDown()

    def test_parse_no_data(self):
        req_parser = request.RawRequest(
            io.BytesIO(data.http_request_no_data.encode("utf8")))
        context, request_data = req_parser.parse_raw_request()
        request_arguments = context.Arguments()
        headers = context.Headers()
        self.assertEqual("GET", request_arguments.get("method"))
        self.assertIn("host", headers)
        self.assertIn("accept", headers)
        self.assertIn("user-agent", headers)
        self.assertEqual(("1", "1"), request_arguments.get("http_version"))
        self.assertEqual(0, len(request_data.read()))
        self.assertIn("something", request_arguments.get("query"))

    def test_parse_no_query(self):
        req_parser = request.RawRequest(
            io.BytesIO(data.http_request_no_query.encode("utf8")))
        context, request_data = req_parser.parse_raw_request()
        request_arguments = context.Arguments()
        headers = context.Headers()
        self.assertEqual("GET", request_arguments.get("method"))
        self.assertIn("host", headers)
        self.assertIn("accept", headers)
        self.assertIn("user-agent", headers)
        self.assertEqual(("1", "1"), request_arguments.get("http_version"))
        self.assertEqual(0, len(request_data.read()))
        self.assertEqual({}, request_arguments.get("query"))

    def test_parse_data(self):
        req_parser = request.RawRequest(io.BytesIO(
            data.http_request_with_query_and_data.encode("utf8")))
        context, request_data = req_parser.parse_raw_request()
        request_arguments = context.Arguments()
        headers = context.Headers()
        self.assertEqual("GET", request_arguments.get("method"))
        self.assertIn("host", headers)
        self.assertIn("content-type", headers)
        self.assertIn("content-length", headers)
        self.assertEqual("11", headers.get("content-length"))
        self.assertIn("user-agent", headers)
        self.assertEqual(("1", "1"), request_arguments.get("http_version"))
        self.assertEqual("hello:hello", request_data.readall().decode())
        self.assertIn("something", request_arguments.get("query"))

    def test_parse_data_with_fn_content_length(self):
        req_parser = request.RawRequest(io.BytesIO(
            data.http_request_with_fn_content_headers.encode("utf8")))
        context, request_data = req_parser.parse_raw_request()
        headers = context.Headers()
        self.assertEqual(len(request_data.read()),
                         int(headers.get("content-length")))
