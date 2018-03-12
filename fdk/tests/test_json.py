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

import datetime as dt
import json
import testtools
import time

from fdk import context
from fdk import runner
from fdk import response
from fdk.tests import data


def dummy_func(ctx, data=None):
    body = json.loads(data) if len(data) > 0 else {"name": "World"}
    return "Hello {0}".format(body.get("name"))


def custom_response(ctx, data=None):
    return response.RawResponse(
        ctx,
        response_data=dummy_func(ctx, data=data),
        status_code=201)


def expectioner(ctx, data=None):
    raise Exception("custom_error")


def none_func(ctx, data=None):
    return


def timed_sleepr(timeout):

    def sleeper(ctx, data=None):
        time.sleep(timeout)

    return sleeper


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

    def test_errored_func(self):
        in_bytes = data.raw_request_without_body.encode('utf8')
        r = runner.handle_request(expectioner, in_bytes)
        self.assertIsNotNone(r)
        self.assertEqual(500, r.status())

    def test_none_func(self):
        in_bytes = data.raw_request_without_body.encode('utf8')
        r = runner.handle_request(none_func, in_bytes)
        self.assertIsNotNone(r)
        self.assertEqual(200, r.status())
        self.assertIn("", r.body())

    def test_deadline(self):
        timeout = 5
        now = dt.datetime.now(dt.timezone.utc).astimezone()
        now += dt.timedelta(0, float(timeout))
        timeout_data = data.json_request_with_body.copy()
        timeout_data["deadline"] = now.isoformat()

        r = runner.handle_request(timed_sleepr(timeout + 1),
                                  json.dumps(timeout_data).encode("utf8"))
        self.assertIsNotNone(r)
        self.assertEqual(502, r.status())
        self.assertIn("function timed out",
                      r.body()["error"]["message"])

    def test_default_deadline(self):
        timeout_data = data.json_request_with_body.copy()
        timeout_data["deadline"] = None

        r = runner.handle_request(timed_sleepr(context.DEFAULT_DEADLINE + 1),
                                  json.dumps(timeout_data).encode("utf8"))
        self.assertIsNotNone(r)
        self.assertEqual(502, r.status())
        self.assertIn("function timed out",
                      r.body()["error"]["message"])
