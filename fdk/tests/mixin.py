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

from fdk import context
from fdk import runner

from fdk.tests import funcs

from xml.etree import ElementTree


class Mixin(object):

    def override_content_type(self, income_data):
        r = runner.from_request(funcs.content_type,
                                income_data,
                                self.format_def)
        r = self.loop.run_until_complete(r)

        self.assertIsNotNone(r)
        h = r.headers()
        self.assertEqual(h.get("content-type"), "application/xml")

    def parse_request_without_data(self, income_data):
        r = runner.from_request(
            funcs.dummy_func, income_data, self.format_def)
        r = self.loop.run_until_complete(r)

        self.assertIsNotNone(r)
        self.assertIn("Hello World", r.body())
        self.assertEqual(200, r.status())

    def parse_request_with_data(self, income_data):
        r = runner.from_request(
            funcs.dummy_func, income_data, self.format_def)
        r = self.loop.run_until_complete(r)

        self.assertIsNotNone(r)
        self.assertIn("Hello John", r.body())
        self.assertEqual(200, r.status())

    def custom_response_object(self, income_data):
        r = runner.from_request(
            funcs.custom_response, income_data, self.format_def)
        r = self.loop.run_until_complete(r)

        self.assertIsNotNone(r)
        self.assertIn("Hello John", r.body())
        self.assertEqual(201, r.status())

    def errored_func(self, income_data):
        r = runner.handle_request(
            funcs.expectioner, income_data, self.format_def)
        r = self.loop.run_until_complete(r)

        self.assertIsNotNone(r)
        self.assertEqual(500, r.status())

    def none_func(self, income_data):
        r = runner.handle_request(
            funcs.none_func, income_data, self.format_def)
        r = self.loop.run_until_complete(r)

        self.assertIsNotNone(r)
        self.assertEqual(200, r.status())
        self.assertIn("", r.body())

    def coro_func(self, income_data):
        r = runner.handle_request(
            funcs.coro, income_data, self.format_def)
        r = self.loop.run_until_complete(r)

        self.assertIsNotNone(r)
        self.assertEqual(200, r.status())
        self.assertIn("hello from coro", r.body())

    def deadline(self, timeout, income_data):
        r = runner.handle_request(
            funcs.timed_sleepr(timeout + 1),
            income_data, self.format_def)
        r = self.loop.run_until_complete(r)

        self.assertIsNotNone(r)
        self.assertEqual(502, r.status())
        self.assertIn("function timed out",
                      r.body()["error"]["message"])

    def default_deadline(self, income_data):
        r = runner.handle_request(
            funcs.timed_sleepr(context.DEFAULT_DEADLINE + 1),
            income_data, self.format_def)
        r = self.loop.run_until_complete(r)

        self.assertIsNotNone(r)
        self.assertEqual(502, r.status())
        self.assertIn("function timed out",
                      r.body()["error"]["message"])

    def xml_successful_verification(self, income_data):
        r = runner.from_request(
            funcs.valid_xml, income_data, self.format_def)
        r = self.loop.run_until_complete(r)
        # this should not raise an error
        ElementTree.fromstring(r.body())
        h = r.headers()
        self.assertEqual(h.get("content-type"), "application/xml")

    def xml_unsuccessful_verification(self, income_data):
        r = runner.from_request(
            funcs.invalid_xml, income_data, self.format_def)
        r = self.loop.run_until_complete(r)
        # this should raise an error
        self.assertRaises(
            ElementTree.ParseError,
            ElementTree.fromstring, r.body()
        )

    def verify_request_headers_through_func(self, income_data):
        r = runner.from_request(funcs.verify_request_headers,
                                income_data,
                                self.format_def)
        r = self.loop.run_until_complete(r)

        self.assertIsNotNone(r)
        h = r.headers()
        self.assertIsNotNone(h.get("Accept"))
        self.assertIsNotNone(h.get("User-Agent"))
