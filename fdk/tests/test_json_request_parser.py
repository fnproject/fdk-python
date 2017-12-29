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

from fdk import headers
from fdk.json import request
from fdk.tests import data


class TestJSONRequestParser(testtools.TestCase):

    def setUp(self):
        super(TestJSONRequestParser, self).setUp()

    def tearDown(self):
        super(TestJSONRequestParser, self).tearDown()

    def test_parse_request_with_data(self):
        req_parser = request.RawRequest(
            io.StringIO(data.json_request_with_data))
        context, request_data = req_parser.parse_raw_request()
        self.assertIsNotNone(context)
        self.assertIsNotNone(request_data)
        self.assertIsInstance(request_data, str)
        self.assertIsInstance(context.Headers(), headers.GoLikeHeaders)

    def test_parse_request_without_data(self):
        req_parser = request.RawRequest(
            io.StringIO(data.json_request_without_data))
        context, request_data = req_parser.parse_raw_request()
        self.assertEqual("", request_data)
