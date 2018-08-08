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
import datetime as dt
import testtools

from fdk.tests import data
from fdk.tests import mixin


class TestJSONRequestParser(mixin.Mixin, testtools.TestCase):

    def setUp(self):
        self.format_def = "json"
        self.loop = asyncio.new_event_loop()
        super(TestJSONRequestParser, self).setUp()

    def tearDown(self):
        self.loop.close()
        super(TestJSONRequestParser, self).tearDown()

    def test_override_content_type(self):
        income_data = data.to_stream(
            data.json_request_without_body)
        self.override_content_type(income_data)

    def test_parse_request_without_data(self):
        income_data = data.to_stream(
            data.json_request_without_body)
        self.parse_request_without_data(income_data)

    def test_parse_request_with_data(self):
        income_data = data.to_stream(
            data.json_request_with_body)
        self.parse_request_with_data(income_data)

    def test_custom_response_object(self):
        income_data = data.to_stream(
            data.json_request_with_body)
        self.custom_response_object(income_data)

    def test_errored_func(self):
        income_data = data.to_stream(
            data.json_request_without_body)
        self.errored_func(income_data)

    def test_none_func(self):
        income_data = data.to_stream(
            data.json_request_without_body)
        self.none_func(income_data)

    def test_coro_func(self):
        income_data = data.to_stream(
            data.json_request_without_body)
        self.coro_func(income_data)

    def test_deadline(self):
        timeout = 5
        now = dt.datetime.now(dt.timezone.utc).astimezone()
        now += dt.timedelta(0, float(timeout))
        timeout_data = data.json_request_with_body.copy()
        timeout_data["deadline"] = now.isoformat()
        self.deadline(timeout, data.to_stream(timeout_data))

    def test_valid_xml(self):
        income_data = data.to_stream(
            data.json_request_without_body)
        self.xml_successful_verification(income_data)

    def test_invalid_xml(self):
        income_data = data.to_stream(
            data.json_request_without_body)
        self.xml_unsuccessful_verification(income_data)

    def test_verify_request_headers(self):
        income_data = data.to_stream(
            data.json_request_without_body)
        self.verify_request_headers_through_func(income_data)
