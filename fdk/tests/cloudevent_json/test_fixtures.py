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

from fdk import fixtures
from fdk.tests import funcs


class TestFuncToTest(fixtures.FunctionTestCase):

    content = "OK"

    def setUp(self):
        super(TestFuncToTest, self).setUp(
            self.content, funcs.content_type)

    def tearDown(self):
        super(TestFuncToTest, self).tearDown()

    def test_response_data(self):
        self.assertResponseConsistent(
            lambda x: x == self.content,
            message="content must be equal to '{0}'"
            .format(self.content)
        )

    def test_response_header_presence(self):
        self.assertInHeaders(
            "content-type",
            message="header 'content-type' "
                    "must be present in headers")

    def test_response_header_value(self):
        self.assertInHeaders(
            "content-type", value='application/xml',
            message="header 'content-type' "
                    "must be present in headers with the exact value")


class TestFuncTimer(fixtures.FunctionTestCase):

    def setUp(self):
        super(TestFuncTimer, self).setUp(
            None, funcs.timed_sleepr(6))

    def tearDown(self):
        super(TestFuncTimer, self).tearDown()

    def test_not_in_time(self):
        self.assertNotInTime(5)

    def test_in_time(self):
        self.assertInTime(8)
