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


from .exceptions import MethodNotSupported, NotFound


from collections import namedtuple
from functools import lru_cache

ROUTER_CACHE_SIZE = 1024
Route = namedtuple(
    "Route", ["handler", "methods", "path"]
)


class Router(object):

    def __init__(self):
        self.__router_map = {}

    def add(self, path, methods, handler):
        self.__router_map[path] = Route(
            handler=handler, methods=methods, path=path)

    @lru_cache(maxsize=ROUTER_CACHE_SIZE)
    def get(self, request_path, request_method):
        try:
            rt = self.__router_map[request_path]
            if request_method not in rt.methods:
                raise MethodNotSupported(
                    "Method {0} for path {1} not allowed"
                    .format(request_method, request_path),
                    request_method, rt.methods)
            return rt.handler, rt.path
        except Exception as ex:
            if isinstance(ex, KeyError):
                raise NotFound(
                    "Route was not registered: {}"
                    .format(request_path))
            else:
                raise ex
