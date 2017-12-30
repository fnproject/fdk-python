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


class GoLikeHeaders(object):

    def __init__(self, headers):
        """
        Go-like headers, this format necessary for Fn
        :param headers: HTTP headers
        """
        if not isinstance(headers, dict):
            raise TypeError("Invalid headers type: {}, only dict allowed."
                            .format(type(headers)))
        for k, v in headers.copy().items():
            del headers[k]
            headers[k.lower().replace("fn_header_", "")] = v
        self.__headers = headers

    def get(self, key, default=None):
        """

        :param key:
        :param default:
        :return:
        """
        if key in self.__headers:
            return (self.__headers[key][0]
                    if len(self.__headers[key]) == 1
                    else self.__headers[key])
        else:
            return default

    def set(self, key, value):
        """

        :param key:
        :param value:
        :return:
        """
        if isinstance(value, (str, float, int)):
            self.__headers[key] = [str(value), ]
        if isinstance(value, (list, tuple)):
            self.__headers = value

    def append(self, key, value):
        """

        :param key:
        :param value:
        :return:
        """
        if key in self.__headers:
            current = self.__headers[key]
            if not isinstance(current, (list, tuple)):
                current = [current, ]
            current.append(value)
            self.__headers[key] = current
        else:
            raise KeyError("Missing key: {}".format(key))

    def for_dump(self):
        return self.__headers
