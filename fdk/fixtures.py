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
import io
import os
import uuid
import ujson
import testtools
import datetime as dt

from fdk import response
from fdk import runner


class FunctionTestCase(testtools.TestCase):

    def setUp(self, request_data: object, func, fn_format: str="json"):
        self.fn_format = fn_format
        self.__protocol_frame = self.setup_protocol_frame(request_data)
        self.setup_environment()
        self.__func = func
        self.__func_data = request_data
        self.loop = asyncio.new_event_loop()
        super(FunctionTestCase, self).setUp()

    def tearDown(self):
        self.loop.close()
        super(FunctionTestCase, self).tearDown()

    def setup_environment(self, timeout=None):
        fn_app_name = "fdk-python-unittest"
        call_id = uuid.uuid4().hex
        path = "/fdk-test"

        os.environ.setdefault("FN_TYPE", "sync")
        os.environ.setdefault("FN_FORMAT", self.fn_format)
        os.environ.setdefault("FN_PATH", path)
        os.environ.setdefault("FN_MEMORY", "256")
        os.environ.setdefault("FN_APP_NAME", fn_app_name)
        os.environ.setdefault("FN_REQUEST_URL",
                              "https://fnservice.io/r/{0}{1}".format(
                                  fn_app_name, path))
        os.environ.setdefault("FN_CALL_ID", call_id)
        os.environ.setdefault("FN_METHOD", "POST")
        os.environ.setdefault("FN_DEADLINE", "")

    def setup_protocol_frame(self, request_data, timeout=None):
        fn_app_name = "fdk-python-unittest"
        call_id = uuid.uuid4().hex
        url = ("https://fnproject.io/r/{0}{1}".
               format(fn_app_name, "/fdk-test"))
        method = "POST"

        now = dt.datetime.now(
            dt.timezone.utc).astimezone()
        extended = now + dt.timedelta(
            seconds=timeout if timeout else 30)

        if self.fn_format == "json":
            json_request_with_body = {
                "call_id": call_id,
                "deadline": extended.isoformat(),
                "body": request_data,
                "content_type": "",
                "protocol": {
                    "type": "http",
                    "method": method,
                    "request_url": url,
                    "headers": {
                        "Accept": ["*/*", ],
                        "User-Agent": ["curl/7.54.0"],
                    }
                }
            }
            return io.BytesIO(
                ujson.dumps(
                    json_request_with_body).encode("utf-8"))

        if self.fn_format == "cloudevent":
            cloudevent_request_with_body = {
                "cloudEventsVersion": "0.1",
                "eventID": uuid.uuid4().hex,
                "source": "fdk-python-unittest",
                "eventType": "cloudevent-fdk-python-unittest",
                "eventTypeVersion": "0.1",
                "eventTime": now.isoformat(),
                "schemaURL": "...",
                "contentType": "application/json",
                "extensions": {
                    "deadline": extended.isoformat(),
                    "protocol": {
                        "type": "http",
                        "method": method,
                        "request_url": url,
                        "headers": {
                            "Accept": ["*/*", ],
                            "User-Agent": ["curl/7.54.0"],
                        }
                    }
                },
                "data": request_data
            }
            return io.BytesIO(
                ujson.dumps(
                    cloudevent_request_with_body).encode("utf-8"))

        raise Exception("unknown format")

    def assertInHeaders(self, key, value=None, message=None):
        r = self.loop.run_until_complete(
            runner.handle_request(
                self.__func, self.__protocol_frame, self.fn_format
            )
        )
        if isinstance(r, (response.JSONResponse, response.CloudEventResponse)):
            headers = r.headers
        else:
            headers = r.headers()

        self.assertIn(key, headers)

        if value is not None:
            header_value = headers.get(key)
            self.assertEqual(value, header_value)

    def assertInTime(self, timeout, message=None):
        frame = self.setup_protocol_frame(
            self.__func_data, timeout=timeout)
        r = self.loop.run_until_complete(
            runner.handle_request(
                self.__func, frame, self.fn_format
            )
        )

        self.assertIsNotNone(r)
        self.assertEqual(200, r.status(), message=message)

    def assertNotInTime(self, timeout, message=None):
        frame = self.setup_protocol_frame(
            self.__func_data, timeout=timeout)
        r = self.loop.run_until_complete(
            runner.handle_request(
                self.__func, frame, self.fn_format
            )
        )

        self.assertIsNotNone(r)
        self.assertEqual(
            502, r.status(),
            message="function's response code must be 502, "
                    "but was {0}".format(r.status()))
        self.assertIn("function timed out",
                      r.body()["error"]["message"])

    def assertResponseConsistent(self, response_validator_func, message=None):
        r = self.loop.run_until_complete(
            runner.handle_request(
                self.__func, self.__protocol_frame, self.fn_format
            )
        )

        ok = response_validator_func(r.body())
        self.assertEqual(True, ok, message=message)
