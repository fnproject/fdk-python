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
import fdk
import io
import os
import time

import testtools

from fdk.http import request as hr
from fdk.json import handle as jh
from fdk.http import handle as hh
from fdk.json import request as jr
from fdk import response
from fdk import runner
from fdk.tests import data


def handle(ctx, **kwargs):
    pass


def sleeper(ctx, **kwargs):
    time.sleep(12)


def custom_response(ctx, **kwargs):
    return response.RawResponse(
        ctx,
        status_code=403,
        headers={
            "Content-Type": "text/plain",
        },
        response_data="Forbidden. Bad credentials.",
    )


def error(ctx, **kwargs):
    raise Exception("custom error, should be handled")


# TODO(denismakogon): FUCK, fix this!!!
@fdk.coerce_input_to_content_type
def validate(ctx, **kwargs):
    return response.RawResponse(
        ctx, response_data=isinstance(kwargs.get("data"), dict),
        headers={
            "Content-Type": "text/plain",
        },
        status_code=200,
    )


class TestRequestTypeCoercing(testtools.TestCase):

    def setUp(self):
        super(TestRequestTypeCoercing, self).setUp()

    def tearDown(self):
        super(TestRequestTypeCoercing, self).tearDown()

    def test_http_data_coercing(self):
        req = hr.RawRequest(io.BytesIO(
            data.http_coerce.encode("utf8")))
        ctx, body = req.parse_raw_request()
        resp = hh.normal_dispatch(validate, ctx, data=body)
        self.assertEqual(200, resp.status())
        self.assertIn(b"True", resp.body())

    def test_json_data_coercing(self):
        req = jr.RawRequest(io.StringIO(data.json_request_with_data))
        ctx, body = req.parse_raw_request()
        resp = jh.normal_dispatch(validate, ctx, data=body)
        self.assertEqual(200, resp.status())
        self.assertIn("true", resp.body())


class TestJSONDispatcher(testtools.TestCase):

    def setUp(self):
        super(TestJSONDispatcher, self).setUp()

    def tearDown(self):
        super(TestJSONDispatcher, self).tearDown()

    def run_json_func(self, func):
        req = jr.RawRequest(io.StringIO(data.json_request_with_data))
        ctx, body = req.parse_raw_request()
        return jh.normal_dispatch(func, ctx, data=body)

    def test_json_normal_dispatch(self):
        resp = self.run_json_func(handle)
        self.assertEqual(200, resp.status())

    def test_json_custom_response(self):
        resp = self.run_json_func(custom_response)
        self.assertEqual(403, resp.status())

    def test_json_custom_error(self):
        resp = self.run_json_func(error)
        self.assertEqual(500, resp.status())
        self.assertIn("custom error, should be handled", resp.body())


class TestHTTPDispatcher(testtools.TestCase):

    def setUp(self):
        super(TestHTTPDispatcher, self).setUp()

    def tearDown(self):
        super(TestHTTPDispatcher, self).tearDown()

    def run_http_func(self, func):
        req = hr.RawRequest(io.BytesIO(
            data.http_request_with_query_and_data.encode("utf8")))
        ctx, body = req.parse_raw_request()
        return hh.normal_dispatch(func, ctx, data=body)

    def test_http_normal_dispatch(self):
        resp = self.run_http_func(handle)
        self.assertEqual(200, resp.status())

    def test_http_custom_response(self):
        resp = self.run_http_func(custom_response)
        self.assertEqual(403, resp.status())

    def test_http_custom_error(self):
        resp = self.run_http_func(error)
        self.assertEqual(500, resp.status())
        self.assertIn(b"custom error, should be handled", resp.body())


class TestJSONDeadline(testtools.TestCase):

    def setUp(self):
        super(TestJSONDeadline, self).setUp()

    def tearDown(self):
        super(TestJSONDeadline, self).tearDown()

    def run_json_func(self, func, deadile_is_seconds):
        os.environ.setdefault("FN_FORMAT", "json")
        now = dt.datetime.now(dt.timezone.utc).astimezone()
        deadline = now + dt.timedelta(seconds=deadile_is_seconds)
        r = "".join((data.json_with_deadline[0],
                     ',"deadline":"{}"\n'.format(deadline.isoformat()),
                     data.json_with_deadline[1]))
        req = jr.RawRequest(io.StringIO(r))
        write_stream = io.StringIO()
        runner.proceed_with_streams(
            func, req, write_stream, jh.normal_dispatch)
        return write_stream.getvalue()

    def test_json_with_deadline(self):
        raw = self.run_json_func(handle, 30)
        self.assertIn('"status_code":200', raw)

    def test_json_timeout_by_deadline(self):
        raw = self.run_json_func(sleeper, 10)
        self.assertIn('"status_code":502', raw)
        self.assertIn('Function timed out', raw)


class TestHTTPDeadline(testtools.TestCase):
    def setUp(self):
        super(TestHTTPDeadline, self).setUp()

    def tearDown(self):
        super(TestHTTPDeadline, self).tearDown()

    def run_http_func(self, func, deadile_is_seconds):
        os.environ.setdefault("FN_FORMAT", "http")
        now = dt.datetime.now(dt.timezone.utc).astimezone()
        deadline = now + dt.timedelta(seconds=deadile_is_seconds)
        with_deadline = data.http_with_deadline.format(deadline.isoformat())
        req = hr.RawRequest(
            io.BytesIO(with_deadline.encode("utf8")))
        write_stream = io.BytesIO(bytes())
        runner.proceed_with_streams(
            func, req, write_stream, hh.normal_dispatch)
        return write_stream.getvalue().decode("utf-8")

    def test_http_with_deadline(self):
        raw = self.run_http_func(handle, 30)
        self.assertIn("200 OK", raw)

    def test_http_timeout_by_deadline(self):
        raw = self.run_http_func(sleeper, 10)
        self.assertIn("502 Bad Gateway", raw)
        self.assertIn("Function timed out", raw)
