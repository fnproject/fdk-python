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

from fdk import errors


class RequestContext(object):

    def __init__(self, app_name, route, call_id,
                 fntype, execution_type=None, deadline=None,
                 config=None, headers=None, arguments=None):
        """
        Request context here to be a placeholder
        for request-specific attributes
        """
        self.__app_name = app_name
        self.__app_route = route
        self.__call_id = call_id
        self.__config = config if config else {}
        self.__headers = headers if headers else {}
        self.__arguments = {} if not arguments else arguments
        self.__type = fntype
        self.__exec_type = execution_type
        self.__deadline = deadline

    def AppName(self):
        return self.__app_name

    def Route(self):
        return self.__app_route

    def CallID(self):
        return self.__call_id

    def Config(self):
        return self.__config

    def Headers(self):
        return self.__headers

    def Arguments(self):
        return self.__arguments

    def Type(self):
        return self.__type

    def Deadline(self):
        return self.__deadline

    def ExecutionType(self):
        return self.__exec_type


class HTTPContext(RequestContext):

    def __init__(self, app_name, route,
                 call_id, fntype="http",
                 deadline=None, execution_type=None,
                 config=None, headers=None,
                 method=None, url=None,
                 query_parameters=None,
                 version=None):
        arguments = {
            "method": method,
            "URL": url,
            "query": query_parameters,
            "http_version": version
        }
        self.DispatchError = errors.HTTPDispatchException
        super(HTTPContext, self).__init__(
            app_name, route, call_id, fntype,
            execution_type=execution_type, deadline=deadline,
            config=config, headers=headers, arguments=arguments)


class JSONContext(RequestContext):

    def __init__(self, app_name, route, call_id,
                 fntype="json", deadline=None,
                 execution_type=None, config=None,
                 headers=None):
        self.DispatchError = errors.JSONDispatchException
        super(JSONContext, self).__init__(
            app_name, route, call_id, fntype,
            execution_type=execution_type,
            deadline=deadline, config=config, headers=headers)


def fromType(fntype, *args, **kwargs):
    if fntype == "json":
        return JSONContext(*args, **kwargs)
    if fntype == "http":
        return HTTPContext(*args, **kwargs)
