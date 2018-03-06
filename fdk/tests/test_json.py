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

import json
import testtools

from fdk import runner
from fdk import response
from fdk.tests import data


def dummy_func(ctx, data=None, loop=None):
    body = json.loads(data) if len(data) > 0 else {"name": "World"}
    return "Hello {0}".format(body.get("name"))


def custom_response(ctx, data=None, loop=None):
    return response.RawResponse(
        ctx,
        response_data=dummy_func(ctx, data=data, loop=loop),
        status_code=201)


class TestJSONRequestParser(testtools.TestCase):

    def setUp(self):
        super(TestJSONRequestParser, self).setUp()

    def tearDown(self):
        super(TestJSONRequestParser, self).tearDown()

    def test_parse_request_without_data(self):
        r = runner.from_request(
            dummy_func, data.json_request_without_body)
        self.assertIsNotNone(r)
        self.assertIn("Hello World", r.body())
        self.assertEqual(200, r.status())

    def test_parse_request_with_data(self):
        r = runner.from_request(
            dummy_func, data.json_request_with_body)
        self.assertIsNotNone(r)
        self.assertIn("Hello John", r.body())
        self.assertEqual(200, r.status())

    def test_custom_response_object(self):
        r = runner.from_request(custom_response, data.json_request_with_body)
        self.assertIsNotNone(r)
        self.assertIn("Hello John", r.body())
        self.assertEqual(201, r.status())
