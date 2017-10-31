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

import dill
import functools
import os
import requests
import types

from fdk.application import errors


def fn_app(fn_app_class):
    """
    Sets up Fn app with config

    @fn_app
    class MyApp(object):

        def __init__(self, *args, **kwargs):
            pass

        @fn_route(
            fn_image="denismakogon/hot-json-python:0.0.1",
            fn_type="sync",
            fn_memory=256,
            fn_format="json",
            fn_timeout=60,
            fn_idle_timeout=200,
        )
        def do_stuff(self, *args, fn_data=None, **kwargs):
            pass

    :param fn_app_class: any class
    :return: class decorator
    """
    @functools.wraps(fn_app_class)
    def wrapper(*args, **kwargs):
        app_name = fn_app_class.__name__
        fn_api_url = os.environ.get("API_URL")
        requests.get(fn_api_url).raise_for_status()
        fn_app_url = "{}/v1/apps/{}".format(
            fn_api_url, app_name.lower())
        del_resp = requests.delete(fn_app_url)
        if del_resp.status_code != 404:
            del_resp.close()
            del_resp.raise_for_status()
        requests.post(
            "{}/v1/apps".format(fn_api_url),
            json={
                "app": {
                    "name": app_name.lower(),
                    "config": kwargs.get("config"),
                },
            }
        ).raise_for_status()
        return fn_app_class(*args)

    return wrapper


def fn(fn_type=None, fn_timeout=60, fn_idle_timeout=200, fn_memory=256,
       dependencies=None):
    """
    Runs Python's function on general purpose Fn function


    What it does?

     Decorator does following:
       - collects dat for Fn route and creates it
       - when function called, that function transforms
         into byte array (Pickle) then gets sent to general
         purpose Fn Python3 function
       - each external dependency (3rd-party libs)
         that are required for func gets transformed
         into byte array (Pickle)

     It means that functions does't run locally but on Fn.

    How is it different from other Python FDK functions?

     - This function works with serialized Python callable objects via wire.
       Each function supplied with set of external dependencies that are
       represented as serialized functions, no matter if they are module-level,
       class-level Python objects

    :param fn_type: Fn function call type
    :type fn_type: str
    :param fn_timeout: Fn function call timeout
    :type fn_timeout: int
    :param fn_idle_timeout: Fn function call idle timeout
    :type fn_idle_timeout: int
    :param fn_memory: Fn function memory limit
    :type fn_memory: int
    :param dependencies: Python's function 3rd-party callable dependencies
    :type dependencies: dict
    :return:
    """
    fn_method = "POST"
    fn_image = "denismakogon/python3-fn-gpi:0.0.1"
    fn_format = "http"
    dependencies = dependencies if dependencies else {}

    def ext_wrapper(action):
        @functools.wraps(action)
        def inner_wrapper(*f_args, **f_kwargs):
            fn_api_url = os.environ.get("API_URL")
            requests.get(fn_api_url).raise_for_status()
            self = f_args[0]
            fn_path = action.__name__.lower()
            if not hasattr(action, "__path_created"):
                fn_routes_url = "{}/v1/apps/{}/routes".format(
                    fn_api_url, self.__class__.__name__.lower())
                resp = requests.post(fn_routes_url, json={
                    "route": {
                        "path": "/{}".format(fn_path),
                        "image": fn_image,
                        "memory": fn_memory if fn_memory else 256,
                        "type": fn_type if fn_type else "sync",
                        "format": fn_format if fn_format else "default",
                        "timeout": fn_timeout if fn_timeout else 60,
                        "idle_timeout": (fn_idle_timeout if
                                         fn_idle_timeout else 120),
                    },
                })

                try:
                    resp.raise_for_status()
                except requests.HTTPError:
                    resp.close()
                    return Exception(resp.content)

                setattr(action, "__path_created", True)

            fn_path = action.__name__.lower()
            fn_exec_url = "{}/r/{}/{}".format(
                fn_api_url, self.__class__.__name__.lower(), fn_path)

            action_in_bytes = dill.dumps(action, recurse=True)
            self_in_bytes = dill.dumps(self, recurse=True)

            for name, method in dependencies.items():
                dependencies[name] = list(dill.dumps(method, recurse=True))

            f_kwargs.update(dependencies=dependencies)
            req = requests.Request(
                method=fn_method, url=fn_exec_url,
                json={
                    "is_coroutine": isinstance(action, types.CoroutineType),
                    "action": list(action_in_bytes),
                    "self": list(self_in_bytes),
                    "args": f_args[1:],
                    "kwargs": f_kwargs,
                }
            )
            session = requests.Session()
            resp = session.send(req.prepare())

            try:
                resp.raise_for_status()
            except requests.HTTPError:
                resp.close()
                return None, errors.FnError(
                    "{}/{}".format(self.__class__.__name__.lower(), fn_path),
                    resp.content)

            resp.close()
            return dill.loads(resp.content), None

        return inner_wrapper

    return ext_wrapper


def with_fn(fn_image=None, fn_type=None,
            fn_memory=256, fn_format=None,
            fn_timeout=60, fn_idle_timeout=200,
            fn_method="GET"):
    """
    Sets up Fn app route based on parameters given above
    :param fn_image: Docker image
    :type fn_image: str
    :param fn_type: Fn route type (async/sync)
    :type fn_type: str
    :param fn_memory: Fn RAM to allocate
    :type fn_memory: int
    :param fn_format: Fn route format to accept
    :type fn_format: str
    :param fn_timeout: Fn route call timeout
    :type fn_timeout: int
    :param fn_idle_timeout: Fn route idle timeout (timeout between calls)
    :type fn_idle_timeout: int
    :param fn_method: HTTP method to use when calling Fn function
    :type fn_method: str
    :return: monkey-patched action (almost the same as decorated)
    """

    def ext_wrapper(action):
        @functools.wraps(action)
        def inner_wrapper(*f_args, **f_kwargs):
            fn_api_url = os.environ.get("API_URL")
            requests.get(fn_api_url).raise_for_status()
            self = f_args[0]
            fn_path = action.__name__.lower()
            # TODO(xxx): hate code duplicates but extracting common function
            # to create a route breaks dill routine somehow
            # need to figure out how and fix that!
            if not hasattr(action, "__path_created"):
                fn_routes_url = "{}/v1/apps/{}/routes".format(
                    fn_api_url, self.__class__.__name__.lower())
                resp = requests.post(fn_routes_url, json={
                    "route": {
                        "path": "/{}".format(fn_path),
                        "image": fn_image,
                        "memory": fn_memory if fn_memory else 256,
                        "type": fn_type if fn_type else "sync",
                        "format": fn_format if fn_format else "default",
                        "timeout": fn_timeout if fn_timeout else 60,
                        "idle_timeout": (fn_idle_timeout if
                                         fn_idle_timeout else 120),
                    },
                })

                try:
                    resp.raise_for_status()
                except requests.HTTPError:
                    resp.close()
                    return Exception(resp.content)

                setattr(action, "__path_created", True)

            fn_path = action.__name__.lower()
            fn_exec_url = "{}/r/{}/{}".format(
                fn_api_url, self.__class__.__name__.lower(), fn_path)
            req = requests.Request(method=fn_method,
                                   url=fn_exec_url,
                                   json=f_kwargs)
            session = requests.Session()
            resp = session.send(req.prepare())

            try:
                resp.raise_for_status()
            except requests.HTTPError:
                resp.close()
                return None, errors.FnError(
                    "{}/{}".format(self.__class__.__name__.lower(), fn_path),
                    resp.content)

            f_kwargs.update(fn_data=resp.text)

            resp.close()
            return action(*f_args, **f_kwargs), None

        return inner_wrapper

    return ext_wrapper
