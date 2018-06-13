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

import testtools

from fdk.headers import GoLikeHeaders


class TestHeaders(testtools.TestCase):

    def test_headers(self):
        header_dict = {
            "Accept": "*/*",
            "User-Agent": "curl/7.54.0",
            "Content-Type": ["text/plain"]
        }
        headers = GoLikeHeaders(header_dict)

        self.assertEqual(headers.for_dump(),
                         self.to_go_like_headers(header_dict))

    def to_go_like_headers(self, headers):
        return {k: v if isinstance(v, (list, tuple)) else [v]
                for k, v in headers.items()}
