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


class RequestContext(object):

    def __init__(self, method=None, url=None,
                 query_parameters=None, headers=None,
                 version=None):
        """
        Request context here to be a placeholder
        for request-specific attributes
        :param method: HTTP request method
        :type method: str
        :param url: HTTP request URL
        :type url: str
        :param query_parameters: HTTP request query parameters
        :type query_parameters: dict
        :param headers: HTTP request headers
        :type headers: object
        :param version: HTTP proto version
        :type version: tuple
        """
        # TODO(xxx): app name, path, memory, type, config
        self.method = method
        self.url = url
        self.query_parameters = query_parameters
        self.headers = headers
        self.version = version
