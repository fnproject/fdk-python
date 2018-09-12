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
import ujson

from fdk import parser

from fdk.tests import data


class TestJSONParser(testtools.TestCase):

    def setUp(self):
        super(TestJSONParser, self).setUp()

    def tearDown(self):
        super(TestJSONParser, self).tearDown()

    def test_parser(self):
        d = ujson.dumps(data.cloudevent_request_without_body)
        encoded = io.BytesIO(("\n\n\n\n\n\n\n\n\n\n\n\n" + d).encode())
        parsed_data = parser.read_json(encoded)

        self.assertIsNotNone(parsed_data)
        self.assertIsInstance(parsed_data, dict)
