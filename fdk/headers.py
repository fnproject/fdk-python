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

from fdk import constants


class GoLikeHeaders(object):

    def __init__(self, headers):
        """
        Go-like headers, this format necessary for Fn
        :param headers: HTTP headers
        """
        if not isinstance(headers, dict):
            raise TypeError("Invalid headers type: {}, only dict allowed."
                            .format(type(headers)))
        self.__headers = {}

        for k, v in headers.copy().items():
            self.set(k, v)

    def __contains__(self, item: str):
        """
        Implements `if ... in ...` protocol on headers
        :param item: header key
        :type item: str
        :return: true/false whether header key is headers
        :rtype: bool
        """
        return item in self.__headers

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
        if not isinstance(value, (list, tuple)):
            value = [str(value), ]
        self.__headers[key] = value

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

    def http_raw(self):
        raw_headers = {}
        headers = self.for_dump()
        for k, v in headers.items():
            if isinstance(v, list):
                raw_headers[k] = ", ".join(headers.get(k))

        return raw_headers

    def delete(self, key):
        if self.get(key) is not None:
            del self.__headers[key]

    def __iter__(self):
        return iter(self.__headers.items())

    def keys(self):
        return self.__headers.keys()

    def items(self):
        return self.__headers.items()

    def values(self):
        return self.__headers.values()


def decap_headers(hdsr):
    ctx_headers = GoLikeHeaders({})
    for k, v in hdsr.items():
        if k.startswith(constants.FN_HTTP_PREFIX):
            ctx_headers.set(k.lstrip(constants.FN_HTTP_PREFIX), v)
        else:
            ctx_headers.set(k, v)
    return ctx_headers


def encap_headers(headers, status=None, content_type=None):
    new_headers = GoLikeHeaders({})
    for k, v in headers.items():
        if not k.startswith(constants.CONTENT_TYPE):
            new_headers.set(constants.FN_HTTP_PREFIX + k, v)

    if status is not None:
        new_headers.set(constants.FN_HTTP_STATUS, str(status))
    if content_type is not None:
        new_headers.set(constants.CONTENT_TYPE, content_type)
    return new_headers
